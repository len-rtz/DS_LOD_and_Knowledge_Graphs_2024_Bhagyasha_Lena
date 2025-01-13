# Project - Linked Open Data & Knowledge Graphs

## Import of LIDO-Data from the Rijksmuseum into Wikidata Cloud

This project provides a Python script for uploading data from the Rijksmuseum's [LIDO (Lightweight Information Describing Objects)](https://cidoc.mini.icom.museum/working-groups/lido/lido-overview/about-lido/what-is-lido/) records to a Wikibase instance using the Pywikibot library.
The goal of this project was to created Linked Open Data, that can be queried using SPARQL and displayed in a Knowledge Graph.
The repository also includes code for parsing LIDO XML data, filtering specific records, and converting them to JSON format.

The result from our project can be found here:  [Rijksmuseum Photo Knowledge Graph]([https://cidoc.mini.icom.museum/working-groups/lido/lido-overview/about-lido/what-is-lido/](https://photos-rijksmuseum.wikibase.cloud/wiki/Main_Page))

## Requirements

- Python 3.6 or higher
- Pywikibot library
- lxml library
- xmltodict library
- JSON data file (provided in the zip-file, can also be created using rijksmuseum-xml-to-json.ipynb)

## Usage

### XML Processing Overview
To parse LIDO XML files, filter specific records, and convert the extracted data to JSON format, run the script in the following notebook rijksmuseum-xml-to-json.ipynb

It includes functionalities for:
- XML Extraction:
  Reads LIDO records from an XML file, extracts relevant fields (e.g., objectID, title), and creates a subset of records for debugging
- Filtering Records:
  Records can be filtered based on a specific term (in our project "photomechanical print") and saved into a new XML file
- XML to JSON Conversion:
  Converts the extracted XML data to JSON format and saves it as a .json file for easier manipulation
- Exploration of LIDO classes:
  Prints a list of all unique LIDO classes as preparation for the mapping with wikidata-classes
- Simple Record Extraction:
  Extracts simple records with title, creator, and date, saving the results into a JSON file with a specified record limit

### Creating a smaller Subset for Trials
To work with less LIDO classes as well as with less collection records / JSON entities, there is an additional Python Script (create-json-subset.py), which extracts simpler records with only title, creator, date and material/tecnique.
It's saving the results into a JSON file with a specified record limit.

### Uploading to Wikibase Instance
Make sure to configure your Pywikibot settings to connect to the desired Wikibase instance. You may need to adjust the login credentials in the Pywikibot configuration file (user-config.py).

The user-config.py file should follow this structure:
```
family = 'rijksmuseum-cloud'
mylang = 'en'
usernames['rijksmuseum-cloud']['en'] = 'username'  # Replace with your username
password_file = "user-password.py"
```
The user-password.py should look like this:
```
('username', 'password')  # Replace with your actual credentials
```

Data Uploader Functions:
- Defines a custom family RijksmuseumCloudFamily to specify the details of the Wikibase instance
- Maps LIDO fields to Wikidata properties
- Processes records from a JSON file, creating or updating statements in the Wikibase instance

XML Parsing:
The XML processing script streams through the LIDO XML file, extracts records, filters based on object work types, and converts data to JSON format.

Functions:
- "get_nested_value(data, path)": Navigates a nested dictionary to retrieve a value using a specified path
- "format_claim_target(value, datatype, site)": Formats values for claims based on their datatype
- "create_statement(item, pid, value, datatype)": Creates a wikidate statement for an item with a specific wikidate property
- "search_or_create_item(repo, label, description=None)": Looks for an existing item in the wikibase cloud or creates a new one if it doesn’t exist
- "process_record(record, repo)" Handles a single LIDO record to create or update a corresponding Wikibase item
- "main()": Initializes the execution of the script

### Feel free to modify any section or detail further based on your preferences or specific project requirements!
