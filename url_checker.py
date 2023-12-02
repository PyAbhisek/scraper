import requests
import json

def check_url_status(url):
    try:
        response = requests.head(url, allow_redirects=True)
        status_code = response.status_code
        if 200 <= status_code < 400:
            print(f"The URL {url} is reachable with status code {status_code}.")
        elif status_code == 404:
            print(f"The URL {url} was not found (status code 404).")
        else:
            print(f"The URL {url} returned a non-success status code: {status_code}.")
    except requests.ConnectionError:
        print(f"Failed to connect to the URL {url}.")

# Example usage
json_file_path = "links.json"

with open(json_file_path, 'r') as json_file:
    data = json.load(json_file)
    urls_to_check = data["links"]

for url in urls_to_check:
    check_url_status(url)
