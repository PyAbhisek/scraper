import json
from selenium import webdriver
from selenium.common import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load configuration from config.json
with open('lotusherbals1_links.json') as f:
    scraping_targets = json.load(f)["links"]

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")

# Path to ChromeDriver executable in Colab
chrome_driver_path = '/usr/bin/google-chrome'

driver = webdriver.Chrome(options=chrome_options)

# Use a list to store all links
all_links = []

# Initialize a URL counter
url_counter = 0

for url in scraping_targets:
    # Increment the URL counter
    url_counter += 1

    print(f"Processing URL {url_counter}/{len(scraping_targets)}: {url}")  # Print the URL being processed

    wait = WebDriverWait(driver, 10)

    driver.get(url)
    print(url)

    cards = driver.find_elements(By.CSS_SELECTOR, ".ProductItem__ImageWrapper.ProductItem__ImageWrapper--withAlternateImage")

    # If there are no cards, skip to the next target
    if not cards:
        print(f"No cards found for URL: {url}")
        continue

    # Keywords to exclude
    exclude_keywords = ['lip-juicers', '-in-1', 'kajal', 'casing', 'lip-gloss', 'brush', 'concealer', 'changing',
                        'refillable-case', 'pencil', 'lip-liner', 'lipliner', 'lip-plumper', 'lip-oil',
                        'multi-mousse', 'lip-balm', 'lip-care', 'cheek-stain', 'cheek', 'scrub',
                        'crayon', 'pack', 'combo', 'fab5', 'lacquer', 'mini','balm','#']

    base_url = "https://www.lotusherbals.com"

    for card in cards:
        try:
            href = card.get_attribute("href")

            if href is not None and not any(keyword in href.lower() for keyword in exclude_keywords):
                if href.startswith("/"):
                    href = base_url + href  # Concatenate base_url and relative href
                all_links.append(href)
        except StaleElementReferenceException:
            # Handle the stale element exception by re-finding the card element
            card = driver.find_element(By.CSS_SELECTOR, ".ProductItem__ImageWrapper.ProductItem__ImageWrapper--withAlternateImage")
            href = card.get_attribute("href")
            print(href)

            if href is not None and not any(keyword in href.lower() for keyword in exclude_keywords):
                if href.startswith("/"):
                    href = base_url + href  # Concatenate base_url and relative href
                    print(href)
                all_links.append(href)


# Step 1: Create a dictionary to store all the links
data = {"links": all_links}

# Step 2: Save all the links to a JSON file
output_filename = "lotusherbals_links.json"
with open(output_filename, "w") as json_file:
    json.dump(data, json_file)

driver.quit()
