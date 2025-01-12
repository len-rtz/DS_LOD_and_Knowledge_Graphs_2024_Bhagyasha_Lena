import pywikibot
import json

# Define your Wikibase instance details
wikibase_url = "https://rijksmuseum.wikibase.cloud"
lang_code = "en"


def create_property_if_missing(repo, label, description, data_type):
    # Search for an existing property
    for prop in repo.all_properties():
        if prop.labels.get('en') == label:
            print(f"Property already exists: {label} ({prop.id})")
            return prop.id

    # Create the property if missing
    new_property = pywikibot.PropertyPage(repo)
    new_property.editEntity({
        "labels": {"en": label},
        "descriptions": {"en": description},
        "datatype": data_type
    })
    print(f"Created property: {label} ({new_property.id})")
    return new_property.id

def create_item_if_missing(repo, label, description):
    # Search for the item
    search_results = repo.search_entities(label, "en")
    if search_results:
        print(f"Item already exists: {label} ({search_results[0]['id']})")
        return search_results[0]['id']

    # Create the item if missing
    new_item = pywikibot.ItemPage(repo)
    new_item.editEntity({
        "labels": {"en": label},
        "descriptions": {"en": description}
    })
    print(f"Created item: {label} ({new_item.id})")
    return new_item.id

def upload_data_from_sdata(data_file, repo):
    # Define properties
    title_property = create_property_if_missing(repo, "Title", "The title of an artwork", "monolingualtext")
    creator_property = create_property_if_missing(repo, "Creator", "The creator of the artwork", "wikibase-item")
    date_property = create_property_if_missing(repo, "Date of inception", "The date the artwork was created", "time")
    material_property = create_property_if_missing(repo, "Material used", "Material used in the artwork", "wikibase-item")
    repository_property = create_property_if_missing(repo, "Location", "The repository where the artwork is stored", "wikibase-item")
    event_type_property = create_property_if_missing(repo, "Type of Event", "Type of event related to the artwork", "wikibase-item")

    # Load data
    with open(data_file, "r") as file:
        data = json.load(file)

    for record in data["records"]:
        try:
            # Create the creator item
            creator_item = create_item_if_missing(repo, record["creator"]["name"], "An artist or creator")
            material_item = create_item_if_missing(repo, record["material"], "Material used in artworks")
            repository_item = create_item_if_missing(repo, record["repository"]["name"], "A repository or museum")

            # Create the artwork item
            artwork = pywikibot.ItemPage(repo)
            artwork.editEntity({
                "labels": {"en": record["title"]},
                "descriptions": {"en": "An artwork in the Rijksmuseum"}
            })

            # Add statements
            # Title
            claim = pywikibot.Claim(repo, title_property)
            claim.setTarget(pywikibot.WbMonolingualText(record["title"], "en"))
            artwork.addClaim(claim)

            # Creator
            claim = pywikibot.Claim(repo, creator_property)
            claim.setTarget(pywikibot.ItemPage(repo, creator_item))
            artwork.addClaim(claim)

            # Date
            if "date" in record:
                claim = pywikibot.Claim(repo, date_property)
                claim.setTarget(pywikibot.WbTime(year=int(record["date"])))
                artwork.addClaim(claim)

            # Material
            claim = pywikibot.Claim(repo, material_property)
            claim.setTarget(pywikibot.ItemPage(repo, material_item))
            artwork.addClaim(claim)

            # Repository Location
            claim = pywikibot.Claim(repo, repository_property)
            claim.setTarget(pywikibot.ItemPage(repo, repository_item))
            artwork.addClaim(claim)

            print(f"Uploaded record: {record['title']}")

        except Exception as e:
            print(f"Error uploading record {record['id']}: {e}")

# Usage
#site = pywikibot.Site("wikibase", "en")  # Replace with your Wikibase instance details
#repo = site.data_repository()

# Hardcode the site connection
site = pywikibot.Site(url=wikibase_url, code=lang_code)
repo = site.data_repository()

upload_data_from_sdata("s1_data.json", repo)
