import json

def extract_simple_records(input_file, output_file, record_limit=500):
    # Open the input file with UTF-8 encoding
    with open(input_file, "r", encoding="utf-8") as file:
        data = json.load(file)
    
    records = data.get("records", {}).get("lido:lido", [])
    simple_records = []

    for record in records:
        try:
            # Filter for records with title, creator, and date
            title = record.get("lido:descriptiveMetadata", {}).get("lido:objectIdentificationWrap", {}).get("lido:titleWrap", {}).get("lido:titleSet", [{}])[0].get("lido:appellationValue", [{}])[0].get("#text", "")
            creator = record.get("lido:descriptiveMetadata", {}).get("lido:eventWrap", {}).get("lido:eventSet", [{}])[0].get("lido:event", {}).get("lido:eventActor", {}).get("lido:actorInRole", {}).get("lido:actor", {}).get("lido:nameActorSet", {}).get("lido:appellationValue", [{}])[0].get("#text", "")
            date = record.get("lido:descriptiveMetadata", {}).get("lido:eventWrap", {}).get("lido:eventSet", [{}])[0].get("lido:event", {}).get("lido:eventDate", {}).get("lido:date", {}).get("lido:earliestDate", "")
            
            if title and creator and date:
                simple_records.append(record)
        except KeyError:
            continue  # Skip incomplete records

    # Limit to record_limit
    simple_records = simple_records[:record_limit]
    
    # Save smaller dataset with UTF-8 encoding
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump({"records": {"lido:lido": simple_records}}, file, indent=4)

# Example usage
extract_simple_records("C:/Users/patil/.vscode/data.json", "C:/Users/patil/.vscode/s1_data.json", record_limit=2)
print("File Saved")
