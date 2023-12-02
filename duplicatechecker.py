import json

def hashable_entry(entry):
    if isinstance(entry, dict):
        return tuple((k, hashable_entry(v)) for k, v in entry.items())
    elif isinstance(entry, list):
        return tuple(hashable_entry(item) for item in entry)
    else:
        return entry

def find_duplicates(json_data):
    seen_entries = {}

    for entry in json_data:
        entry_tuple = hashable_entry(entry)

        # Check if the entry is unique based on all fields
        if entry_tuple not in seen_entries:
            seen_entries[entry_tuple] = 1
        else:
            seen_entries[entry_tuple] += 1

    return seen_entries

# Specify the path to your JSON file
json_file_path = '/Users/cepl/Desktop/scraping/scraper/01-12-2023/partial_scraped_data.json'

# Load JSON data from the file
with open(json_file_path, 'r') as file:
    input_json = json.load(file)

# Call the find_duplicates function
duplicate_count = find_duplicates(input_json)

# Display only the duplicate entries
print("Duplicate entries:")
for entry, count in duplicate_count.items():
    if count > 1:
        print(f"{entry}: {count} occurrences")
