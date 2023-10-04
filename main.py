import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load configuration from config.json
with open("config.json", "r") as config_file:
    config_data = json.load(config_file)

# Keywords to exclude
exclude_keywords = ['lip-juicers', '-in-1', 'kajal', 'casing', 'lip-gloss', 'brush', 'concealer', 'changing',
                   'refillable-case', 'pencil', 'lip-liner', 'lipliner', 'lip-plumper', 'lip-oil', 'multi-mousse',
                   'lip-balm', 'lip-care', 'cheek-stain', 'cheek', 'scrub', 'crayon', 'pack', 'combo', 'fab5',
                   'lacquer', 'mini', 'duo', '-for-1', 'trio', 'combo', 'set', 'tint',
                   'kit','collection']

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")

# Set the viewport size
chrome_options.add_argument("--window-size=1920,1080")

# Path to ChromeDriver executable
chrome_driver_path = '/usr/bin/chromedriver'

# Loop through each configuration
for config in config_data:
    url = config.get("url")
    css_selector = config.get("css_selector")
    filename = config.get("filename")
    startingrange_str = config.get("startingrange")
    endingrange_str = config.get("endingrange")

    if startingrange_str and endingrange_str:
        startingrange = int(startingrange_str)
        endingrange = int(endingrange_str)
        url1 = config.get("first_half_url")
        url2 = config.get("second_half_url")

        # Use a list to temporarily store data
        links = []

        for page_number in range(startingrange, endingrange):
            url = url1 + str(page_number) + url2
            print(url)

            # Create a new WebDriver instance and navigate to the URL
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)

            wait = WebDriverWait(driver, 10)

            # Find elements based on the provided CSS selector
            cards = driver.find_elements(By.CSS_SELECTOR, css_selector)

            # # Use a list to temporarily store data
            # links = []

            # Loop through the found elements
            for card in cards:
                href = card.get_attribute("href")

                # Check if any of the exclude keywords are present in the href
                if not any(keyword in href.lower() for keyword in exclude_keywords):
                    links.append(href)  # Only add the link if it doesn't contain exclude keywords

            driver.quit()

            # Step 1: Create a dictionary to store the data
            data = {"links": links}

            # Step 2: Save the data dictionary to a JSON file with the provided filename
            with open(f"{filename}.json", "w") as json_file:
                json.dump(data, json_file)  # The 'indent' argument is optional for pretty formatting

    else:
        # Create a new WebDriver instance and navigate to the URL
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        wait = WebDriverWait(driver, 10)

        # Find elements based on the provided CSS selector
        cards = driver.find_elements(By.CSS_SELECTOR, css_selector)

        # Use a list to temporarily store data
        links = []

        # Loop through the found elements
        for card in cards:
            href = card.get_attribute("href")

            # Check if any of the exclude keywords are present in the href
            if not any(keyword in href.lower() for keyword in exclude_keywords):
                links.append(href)  # Only add the link if it doesn't contain exclude keywords

        driver.quit()

        # Step 1: Create a dictionary to store the data
        data = {"links": links}

        # Step 2: Save the data dictionary to a JSON file with the provided filename
        with open(f"{filename}.json", "w") as json_file:
            json.dump(data, json_file)  # The 'indent' argument is optional for pretty formatting
