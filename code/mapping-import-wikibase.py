import pywikibot
import json
from pywikibot.family import Family

class RijksmuseumCloudFamily(Family):  
    name = 'rijksmuseum-cloud'

    @classmethod 
    def __post_init__(cls):
        cls.langs = {
            'en': 'photos-rijksmuseum.wikibase.cloud'
        }

    def protocol(self, code):
        return 'https'

    def scriptpath(self, code):
        return '/w'
        
    def interface(self, code):
        return 'DataSite'

# PROPERTY_MAPPINGS
PROPERTY_MAPPINGS = {
    "inventory_number": {
        "pid": "P1", 
        "extract_path": ["lido:objectIdentificationWrap", "lido:repositoryWrap", "lido:repositorySet", "lido:workID", "#text"],
        "datatype": "string",
        "required": True
    },
    "title_en": {
        "pid": "P2",
        "extract_path": ["lido:objectIdentificationWrap", "lido:titleWrap", "lido:titleSet", 0, "lido:appellationValue", 0, "#text"],
        "datatype": "monolingualtext",
        "language": "en",
        "required": True
    },
    "title_nl": {
        "pid": "P2",
        "extract_path": ["lido:objectIdentificationWrap", "lido:titleWrap", "lido:titleSet", 0, "lido:appellationValue", 1, "#text"],
        "datatype": "monolingualtext",
        "language": "nl",
        "required": False
    },
    "creator": {
        "pid": "P3",
        "extract_path": ["lido:eventWrap", "lido:eventSet", 0, "lido:event", "lido:eventActor", "lido:actorInRole", "lido:actor", "lido:nameActorSet", "lido:appellationValue", 0, "#text"],
        "datatype": "wikibase-item",
        "required": False
    },
    "inception": {
        "pid": "P4",
        "extract_path": ["lido:eventWrap", "lido:eventSet", 0, "lido:event", "lido:eventDate", "lido:date", "lido:earliestDate"],
        "datatype": "time",
        "required": False
    },
    "materials_tech": {
        "pid": "P5",
        "extract_path": ["lido:eventWrap", "lido:eventSet", 0, "lido:event", "lido:eventMaterialsTech"],
        "datatype": "wikibase-item",
        "required": False
    }
}

def get_nested_value(data, path):
    """Safely navigate nested dictionary using a path list"""
    current = data
    for key in path:
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif isinstance(current, list) and isinstance(key, int) and len(current) > key:
            current = current[key]
        else:
            return None
    return current

def extract_materials_tech(materials_tech_data):
    """Extract materials and techniques from the LIDO structure"""
    if not materials_tech_data or not isinstance(materials_tech_data, list):
        return []
    
    terms = []
    for entry in materials_tech_data:
        if "lido:materialsTech" in entry:
            term_data = entry["lido:materialsTech"].get("lido:termMaterialsTech", {})
            term_list = term_data.get("lido:term", [])
            if isinstance(term_list, dict):  # Single term
                term_list = [term_list]
            for term in term_list:
                if term.get("@xml:lang") == "nl":  # Prioritize Dutch terms
                    terms.append({"value": term.get("#text"), "language": "nl"})
    return terms

def format_claim_target(value, datatype, site, language=None):
    """Format value according to its datatype for use in claims"""
    try:
        if datatype == "monolingualtext":
            return pywikibot.WbMonolingualText(text=str(value), language=language or 'en')
        elif datatype == "time":
            try:
                year = int(value)
            except (ValueError, TypeError):
                print(f"Invalid year value: {value}")
                return None
            return pywikibot.WbTime(year=year, precision=9)
        elif datatype == "wikibase-item":
            return pywikibot.ItemPage(site, value) if isinstance(value, str) else value
        else:  # string or other basic types
            return str(value)
    except Exception as e:
        print(f"Error formatting claim target: {e}")
        return None

def create_statement(item, pid, value, datatype, language=None):
    """Create a statement on an item using a specific property"""
    try:
        claim = pywikibot.Claim(item.site, pid)
        target = format_claim_target(value, datatype, item.site, language)
        if not target:
            print(f"Failed to format target for property {pid}")
            return False
            
        if claim.getTarget() == target:
            print(f"Claim already exists for {pid}, skipping")
            return True
        
        claim.setTarget(target)
        item.addClaim(claim, summary=f"Adding {pid}")
        print(f"Added statement: {pid} = {value}")
        return True
    except Exception as e:
        print(f"Error creating statement: {e}")
        return False

def search_or_create_item(repo, label, description=None, labels=None):
    """Search for an existing item or create a new one"""
    try:
        search_results = list(repo.search_entities(label, language='en'))
        for result in search_results:
            item = pywikibot.ItemPage(repo, result['id'])
            if item.exists() and item.get()['labels'].get('en') == label:
                return item
                
        labels = labels or {"en": label}
        new_item = pywikibot.ItemPage(repo)
        new_item.editEntity({
            "labels": {lang: {"language": lang, "value": value} for lang, value in labels.items()},
            "descriptions": {"en": {"language": "en", "value": description or "Photography from the Collection of the Rijksmuseum Amsterdam"}}
        })
        print(f"Created new item: {label}")
        return new_item
    except Exception as e:
        print(f"Error in search_or_create_item: {e}")
        return None

def process_record(record, repo):
    """Process a single LIDO record and create/update Wikibase item"""
    try:
        desc_metadata = record.get("lido:descriptiveMetadata", {})
        
        # Extract basic information first
        title_en = get_nested_value(desc_metadata, PROPERTY_MAPPINGS["title_en"]["extract_path"])
        title_nl = get_nested_value(desc_metadata, PROPERTY_MAPPINGS["title_nl"]["extract_path"])
        inventory_number = get_nested_value(desc_metadata, PROPERTY_MAPPINGS["inventory_number"]["extract_path"])
        
        if not title_en or not inventory_number:
            print("Missing required title or inventory number")
            return False
            
        print(f"\nProcessing artwork: {title_en} ({inventory_number})")
        
        # Create main artwork item with both language labels
        labels = {"en": title_en}
        if title_nl:
            labels["nl"] = title_nl
        artwork_item = search_or_create_item(repo, title_en, labels=labels)
        if not artwork_item:
            return False
            
        # Add inventory number statement 
        create_statement(artwork_item, PROPERTY_MAPPINGS["inventory_number"]["pid"], inventory_number, "string")
        
        # Add title statements in both languages
        create_statement(artwork_item, PROPERTY_MAPPINGS["title_en"]["pid"], title_en, "monolingualtext", "en")
        if title_nl:
            create_statement(artwork_item, PROPERTY_MAPPINGS["title_nl"]["pid"], title_nl, "monolingualtext", "nl")
        
        # Process materialsTech
        materials_tech_data = get_nested_value(desc_metadata, PROPERTY_MAPPINGS["materials_tech"]["extract_path"])
        if materials_tech_data:
            materials_terms = extract_materials_tech(materials_tech_data)
            for term_data in materials_terms:
                term = term_data["value"]
                language = term_data["language"]
                material_item = search_or_create_item(repo, term)
                if material_item:
                    material_label = {"language": language, "value": term}
                    material_item.editLabels(labels={language: material_label}, summary=f"Adding {language} label for material")
                    create_statement(artwork_item, PROPERTY_MAPPINGS["materials_tech"]["pid"], material_item, "wikibase-item")
        
        # Add other statements based on mapping
        for prop_name, mapping in PROPERTY_MAPPINGS.items():
            if prop_name in ("title_en", "title_nl", "inventory_number", "materials_tech"):
                continue  # Already handled these
            value = get_nested_value(desc_metadata, mapping["extract_path"])
            if value:
                if prop_name == "inception":
                    try:
                        int(value)
                    except (ValueError, TypeError):
                        print(f"Skipping invalid inception value: {value}")
                        continue
                if mapping["datatype"] == "wikibase-item":
                    value = search_or_create_item(repo, value)
                create_statement(artwork_item, mapping["pid"], value, mapping["datatype"])
        
        print(f"Successfully processed artwork: {title_en}")
        return True
        
    except Exception as e:
        print(f"Error processing record: {e}")
        return False

def main():
    pywikibot.config.family_files['rijksmuseum-cloud'] = 'rijksmuseum_family.py' 
    pywikibot.Family._families['rijksmuseum-cloud'] = RijksmuseumCloudFamily()
    
    site = pywikibot.Site('en', 'rijksmuseum-cloud')
    site.login()
    
    repo = site.data_repository()
    
    print("Starting data upload...")

    with open("first-50.json", "r", encoding='utf-8') as file:
        data = json.load(file)

    records = data.get("records", {}).get("lido:lido", [])
    print(f"Found {len(records)} records to process")

    for record in records:
        process_record(record, repo)

    print("Finished processing all records")
        
if __name__ == "__main__":
    main()
