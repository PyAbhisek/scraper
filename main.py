import json
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
chrome_driver_path = '/usr/bin/chromedriver'

# Create the Chrome WebDriver instance with the Service and Options
driver = webdriver.Chrome(options=chrome_options)



for target in scraping_targets:
    url = target["url"]
    class_name = target["css_selector"]
    filename_prefix = target["filename"]
    loadmore = target.get('loadmore', '')  # Use get method with a default value
    base_url = target.get('base_url', '')  # Use get method with a default value
    startingrange = target.get('startingrange', '')  # Use get method with a default value
    endingrange = target.get('endingrange', '')  # Use get method with a default value
    parent_element = target.get('parent_element', '')  # Use get method with a default value
    wait = WebDriverWait(driver, 40)

    driver.get(url)

    if loadmore:
        try:
            pagination_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, loadmore)))
            pagination_button.click()
            print("clicked")
        except TimeoutException:
            print(f"TimeoutException: Pagination button not found for URL: {url}")

    try:
        if parent_element:
            parent_css = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, parent_element)))
            cards = parent_css.find_elements(By.CSS_SELECTOR, class_name)
        else:
            cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, class_name)))
    except TimeoutException:
        print(f"TimeoutException: No cards found for URL: {url}")
        continue

    links_set = set()

    exclude_keywords = ['lip-juicers', '-in-1', 'kajal', 'casing', 'lip-gloss', 'brush', 'concealer', 'changing',
                        'refillable-case', 'pencil', 'lip-liner', 'lipliner', 'lip-plumper', 'lip-oil',
                        'multi-mousse', 'lip-balm', 'lip-care', 'cheek-stain', 'cheek', 'scrub',
                        'crayon', 'pack', 'combo', 'fab5', 'lacquer', 'mini', 'duo', '-for-1', 'trio']
    for card in cards:
        try:
            href = card.get_attribute("href")
            if href is not None and not any(keyword in href.lower() for keyword in exclude_keywords):
                if href.startswith("/"):
                    href = base_url + href
                links_set.add(href)
        except StaleElementReferenceException:
            print("StaleElementReferenceException: Handling stale element reference")
            continue

    links = list(links_set)

    data = {"links": links}

    output_filename = f"{filename_prefix}_links.json"
    with open(output_filename, "w") as json_file:
        json.dump(data, json_file)

driver.quit()
