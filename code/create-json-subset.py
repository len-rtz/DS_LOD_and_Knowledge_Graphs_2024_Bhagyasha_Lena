import json
def extract_simple_records(input_file, output_file, record_limit=10):
    # Open the input file with UTF-8 encoding
    with open(input_file, "r", encoding="utf-8") as file:
        data = json.load(file)
    
    records = data.get("records", {}).get("lido:lido", [])
    simple_records = []
    
    for record in records:
        try:
            # Extract fields
            title = record.get("lido:descriptiveMetadata", {}).get("lido:objectIdentificationWrap", {}).get("lido:titleWrap", {}).get("lido:titleSet", [{}])[0].get("lido:appellationValue", [{}])[0].get("#text", "")
            creator = record.get("lido:descriptiveMetadata", {}).get("lido:eventWrap", {}).get("lido:eventSet", [{}])[0].get("lido:event", {}).get("lido:eventActor", {}).get("lido:actorInRole", {}).get("lido:actor", {}).get("lido:nameActorSet", {}).get("lido:appellationValue", [{}])[0].get("#text", "")
            date = record.get("lido:descriptiveMetadata", {}).get("lido:eventWrap", {}).get("lido:eventSet", [{}])[0].get("lido:event", {}).get("lido:eventDate", {}).get("lido:date", {}).get("lido:earliestDate", "")
            materials_tech = record.get("lido:descriptiveMetadata", {}).get("lido:eventWrap", {}).get("lido:eventSet", [{}])[0].get("lido:event", {}).get("lido:eventMaterialsTech", [])
            
            if title and creator and date and materials_tech:
                simple_records.append(record)
                if len(simple_records) >= record_limit:
                    break
                
        except KeyError:
            continue  # Skip incomplete records
    
    # Save smaller dataset with UTF-8 encoding
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump({"records": {"lido:lido": simple_records}}, file, indent=4)

# Example usage
extract_simple_records("data.json", "first-50.json", record_limit=50)
print("File Saved")
