import json
from selenium import webdriver

from selenium.common import TimeoutException, StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from selenium.webdriver.chrome.options import Options

# Load configuration from config.json
with open('config.json') as f:
    scraping_targets = json.load(f)

options = Options()
options.add_argument("--headless")
options.add_argument("window-size=1400,1500")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("start-maximized")
options.add_argument("enable-automation")
options.add_argument("--disable-infobars")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--single-process")
options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
# Path to ChromeDriver executable in Colab
chrome_driver_path = '/usr/bin/chromedriver'
driver = webdriver.Chrome(options=options)




# Initialize a URL counter
url_counter = 0

for target in scraping_targets:
    url = target["url"]
    class_name = target["css_selector"]
    filename_prefix = target["filename"]
    loadmore = target['loadmore']
    base_url = target['base_url']

    # Increment the URL counter
    url_counter += 1

    print(f"Processing URL {url_counter}/{len(scraping_targets)}: {url}")  # Print the URL being processed

    wait = WebDriverWait(driver, 10)

    driver.get(url)
    print(url)

    if loadmore:

        try:

            pagination_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, loadmore)))

            pagination_button.click()
        except (ElementClickInterceptedException, StaleElementReferenceException):

            pagination_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, loadmore)))
            driver.execute_script("arguments[0].click();", pagination_button)

    cards = driver.find_elements(By.CSS_SELECTOR, class_name)
    # cards= wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, class_name)))

    print(class_name)
    print(cards)

    # If there are no cards, skip to the next target
    if not cards:
        print(f"No cards found for URL: {url}")
        continue

    # Use a set to temporarily store links and remove duplicates
    links_set = set()

    # Keywords to exclude
    exclude_keywords = ['lip-juicers', '-in-1', 'kajal', 'casing', 'lip-gloss', 'brush', 'concealer', 'changing',
                        'refillable-case', 'pencil', 'lip-liner', 'lipliner', 'lip-plumper', 'lip-oil',
                        'multi-mousse', 'lip-balm', 'lip-care', 'cheek-stain', 'cheek', 'scrub',
                        'crayon', 'pack', 'combo', 'fab5', 'lacquer', 'mini']
    iiii = 0
    for card in cards:
        iiii += 1
        print(f"loop {iiii}")
        try:
            href = card.get_attribute("href")
            if href is not None and not any(keyword in href.lower() for keyword in exclude_keywords):
                if href.startswith("/"):
                    href = base_url + href  # Concatenate base_url and relative href
                links_set.add(href)
        except StaleElementReferenceException:
            # Handle the stale element exception by re-finding the card element
            card = driver.find_element(By.CSS_SELECTOR, class_name)
            href = card.get_attribute("href")
            if href is not None and not any(keyword in href.lower() for keyword in exclude_keywords):
                if href.startswith("/"):
                    href = base_url + href  # Concatenate base_url and relative href
                links_set.add(href)

    # Convert the set to a list
    links = list(links_set)

    # Step 1: Create a dictionary to store the links
    data = {"links": links}

    # Step 2: Save the links dictionary to a JSON file
    output_filename = f"{filename_prefix}_links.json"
    with open(output_filename, "w") as json_file:
        json.dump(data, json_file)

driver.quit()
