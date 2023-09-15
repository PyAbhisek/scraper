import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
# Initialize an empty list to store the links
links = []

for page_number in range(1, 54):
    driver = webdriver.Chrome(options=chrome_options)
    website = f'https://www.nykaa.com/makeup/lips/lipstick/c/249?page_no={page_number}&sort=popularity&eq=desktop'

    driver.get(website)

    wait = WebDriverWait(driver, 10)
    cards = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'css-qlopj4')))

    for card in cards:
        href = card.get_attribute("href")
        # if 'kay-beauty-matte-lipstick/p/1010793' in href:
        links.append(href)

    driver.quit()

# Create a dictionary to store the links
data = {"links": links}

# Save the links dictionary to a JSON file
with open("links.json", "w") as json_file:
    json.dump(data, json_file, indent=4)  # The 'indent' argument is optional for pretty formatting

