import json
from selenium import webdriver
from selenium.common import TimeoutException, StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Load configuration from config.json
with open('config.json') as f:
    scraping_targets = json.load(f)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")

# Set the viewport size
chrome_options.add_argument("--window-size=1920,1080")

# Path to ChromeDriver executable in Colab
chrome_driver_path = '/usr/bin/google-chrome'

driver = webdriver.Chrome(options=chrome_options)



# Initialize a URL counter
url_counter = 0

for target in scraping_targets:
  
    url = target["url"]
    class_name = target["css_selector"]
    filename_prefix = target["filename"]
    loadmore = target['loadmore']
    base_url = target['base_url']
    parent_element = target['parent_element']
    wait = WebDriverWait(driver, 10)
    # Increment the URL counter
    url_counter += 1

    print(f"Processing URL {url_counter}/{len(scraping_targets)}: {url}")  # Print the URL being processed

  

    driver.get(url)
    print(url)
    if filename_prefix == "sugarcosmetics":
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'DesktopProductCard_collectionContainer__j0VId'))
        )
        last_height = driver.execute_script('return document.body.scrollHeight')
        while True:
            
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(5)  # Increase the waiting time to slow down scrolling
            new_height = driver.execute_script('return document.body.scrollHeight')
            if new_height == last_height:
                break
            last_height = new_height

    if loadmore:

        try:

            pagination_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, loadmore)))

            pagination_button.click()
        except (ElementClickInterceptedException, StaleElementReferenceException):

            pagination_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, loadmore)))
            driver.execute_script("arguments[0].click();", pagination_button)
    print(parent_element)

    # Assuming 'driver' is your WebDriver instance
    wait = WebDriverWait(driver, 10)  # 10 seconds timeout



    if parent_element:
        
        parent_elm = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, parent_element)))
        if parent_element:
            print(parent_element + "found")
        cards = parent_elm.find_elements(By.CSS_SELECTOR, class_name)
        if cards:
            print("cards found")
    else:
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
                        'crayon', 'pack', 'combo', 'fab5', 'lacquer', 'mini','balm','#','jennifer','DUO']
    iiii = 0
    for card in cards:
        iiii += 1
        print(f"loop {iiii}")
        try:
            href = card.get_attribute("href")
            print(href)
            if href is not None and not any(keyword in href.lower() for keyword in exclude_keywords):
                if href.startswith("/"):
                    href = base_url + href  # Concatenate base_url and relative href
                links_set.add(href)
        except StaleElementReferenceException:
            # Handle the stale element exception by re-finding the card element
            card = driver.find_element(By.CSS_SELECTOR, class_name)
            href = card.get_attribute("href")
            print(href)
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


