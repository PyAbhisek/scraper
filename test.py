import json
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options  # Import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Load configuration from config.json
with open('config.json') as f:
    scraping_targets = json.load(f)

chrome_driver_path = r'C:\Users\abhis\OneDrive\Desktop\pythonselenium\chromedriver-win64\chromedriver.exe'
chrome_service = Service(chrome_driver_path)

# Create ChromeOptions for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")  # Add this line to run headlessly
chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration for headless mode
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")

# Set the viewport size
chrome_options.add_argument("--window-size=1920,1080")  # Adjust viewport size as needed

driver = webdriver.Chrome(service=chrome_service, options=chrome_options)  # Pass the options to the driver

for target in scraping_targets:
    url = target["url"]
    class_name = target["css_selector"]
    filename_prefix = target["filename"]
    loadmore = target['loadmore']
    base_url = target['base_url']
    startingrange = target['startingrange']
    endingrange = target['endingrange']
    parent_element = target.get('parent_element', '')  # Modified to use get method
    wait = WebDriverWait(driver, 40)

    driver.get(url)

    if loadmore:
        try:
            pagination_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, loadmore)))
        except TimeoutException:
            print(f"TimeoutException: Pagination button not found for URL: {url}")
            continue

        # Attempt to click the pagination button, retrying once more if it fails
        try:
            pagination_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, loadmore)))
            pagination_button.click()
        except StaleElementReferenceException:
            print("StaleElementReferenceException: Retrying click on pagination button")
            pagination_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, loadmore)))
            pagination_button.click()

    try:
        if parent_element:
            parent_css = driver.find_element(By.CSS_SELECTOR, parent_element)
            cards = parent_css.find_elements(By.CSS_SELECTOR, class_name)  # Find cards within the parent element
        else:
            cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, class_name)))
    except TimeoutException:
        print(f"TimeoutException: No cards found for URL: {url}")
        continue

    # Use a set to temporarily store links and remove duplicates
    links_set = set()

    # Keywords to exclude
    exclude_keywords = ['lip-juicers','-in-1', 'kajal' ,'casing','lip-gloss', 'brush', 'concealer', 'changing', 'refillable-case', 'pencil',
                        'lip-liner','lipliner', 'lip-plumper', 'lip-oil', 'multi-mousse', 'lip-balm', 'lip-care', 'cheek-stain', 'cheek' ,'scrub',
                        'crayon' ,'pack', 'combo','fab5' ,'lacquer', 'mini' ,'duo', '-for-1' ,'trio']
    for card in cards:
        try:
            href = card.get_attribute("href")
            if href is not None and not any(keyword in href.lower() for keyword in exclude_keywords):
                if href.startswith("/"):
                    href = base_url + href  # Concatenate base_url and relative href
                links_set.add(href)
        except StaleElementReferenceException:
            # Handle stale element reference here, you can choose to ignore it or refresh the element
            print("StaleElementReferenceException: Handling stale element reference")
            continue

    # Convert the set to a list
    links = list(links_set)

    # Step 1: Create a dictionary to store the links
    data = {"links": links}

    # Step 2: Save the links dictionary to a JSON file
    output_filename = f"{filename_prefix}_links.json"
    with open(output_filename, "w") as json_file:
        json.dump(data, json_file)

driver.quit()
