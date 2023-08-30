import os
import json
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException, ElementClickInterceptedException
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from datetime import date

# Load configuration from config.json
with open('BS4Config.json') as f:
    scraping_targets = json.load(f)

# Get the current date in the format "dd/mm/yyyy"
current_date = date.today().strftime("%d-%m-%Y")

# Create a directory with the current date
output_directory = os.path.join(os.getcwd(), current_date)
os.makedirs(output_directory, exist_ok=True)

chrome_driver_path = r'C:\Users\abhis\OneDrive\Desktop\pythonselenium\chromedriver-win64\chromedriver.exe'
chrome_service = Service(chrome_driver_path)

def get_image_rgb(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)
    img = Image.open(BytesIO(response.content))
    width, height = img.size
    img = img.convert('RGB')
    return img.getpixel((width // 2, height // 2))

def click_element_safely(element):
    try:
        element.click()
    except StaleElementReferenceException:
        # Handle the StaleElementReferenceException by re-locating the element before clicking
        click_element_safely(element)

def handle_popups(driver):
    try:
        # Define the XPath for the popup and close button
        popup_xpath = '//*[@id="bik-widget-wrapper-Q0bQgojHaEBAsabJV5Xp"]/div/div'
        close_button_xpath = '//*[@id="bik-widget-wrapper-Q0bQgojHaEBAsabJV5Xp"]/div/div/div[1]/div'

        # Wait for the popup to become visible (timeout after 10 seconds)
        wait = WebDriverWait(driver, 10)
        popup = wait.until(EC.visibility_of_element_located((By.XPATH, popup_xpath)))

        if popup.is_displayed():
            # Handle the pop-up here
            # For example, you can click a close button to dismiss it
            close_button = popup.find_element(By.XPATH, close_button_xpath)
            close_button.click()
    except NoSuchElementException:
        # No pop-up found, continue with scraping
        pass

for target in scraping_targets:
    website_name = target["filename"]  # Use the "filename" as the unique identifier
    all_data = []
    product_name = target["product_name"]
    shade_image_srcset = target["shade_image_srcset"]
    shade_click = target["shade_click"]
    shade_Original_Price = target['shade_Original_Price']
    shade_price = target['shade_price']
    shade_name = target['shade_name']
    image_base_url = target['image_base_url']
    vendor = target['vendor']
    filename_prefix = target["filename"]
    shade_image_src = target["shade_image_src"]
    parent_element = target['parent_element']
    product_name_parent = target['product_name_parent']
    price_parent = target['price_parent']
    img_tag = target['img_tag']
    img_parent = target['img_parent']

    def scrape_data(url):
        driver = webdriver.Chrome(service=chrome_service)
        driver.get(url)

        try:
            driver.implicitly_wait(10)
            product_counter = 0  # Initialize the product_counter
            trigger_popup_after = 2  # Set the number of iterations after which the popup should be triggered

            if parent_element:
                parent = driver.find_element(By.CSS_SELECTOR, parent_element)
                shade_items = parent.find_elements(By.CSS_SELECTOR, shade_click)
            else:
                shade_items = driver.find_elements(By.CSS_SELECTOR, shade_click)

            product_data = {
                "url": url,
                "shades": []
            }

            for shade_item in shade_items:
                product_counter += 1  # Increment the product_counter for each iteration
                print(f"Product #{product_counter}")

                try:
                    shade_item.click()
                except (ElementNotInteractableException, ElementClickInterceptedException):
                    print("Could not click on the shade item (OUT OF STOCK). Skipping to the next one.")
                    continue

                time.sleep(3)
                window_location = driver.execute_script("return window.location.href")
                print(window_location)

                if filename_prefix == "typsybeauty" and product_counter == trigger_popup_after:
                    handle_popups(driver)

                # for shade price
                try:
                    price_match = driver.find_element(By.CSS_SELECTOR, shade_price)
                    price = price_match.text.strip()
                    if not price:
                        price = price_match.get_attribute("textContent").strip()
                    if not price:
                        price = price_match.get_attribute("innerText").strip()
                    print(price)

                except NoSuchElementException:
                    price = "Price not found"
                    print(price)

                # for original shade price
                oprice = ""
                if price_parent:
                    try:
                        parent_price = driver.find_element(By.CSS_SELECTOR, price_parent)
                        originalprice_match = parent_price.find_element(By.CSS_SELECTOR, shade_Original_Price)
                        oprice = originalprice_match.text.strip()
                        print(oprice)
                    except NoSuchElementException:
                        oprice = "Price not found"
                        print(oprice)

                # for product name
                try:
                    if product_name_parent:
                        product_name_parent_container = driver.find_element(By.CSS_SELECTOR, product_name_parent)
                        name_match = product_name_parent_container.find_element(By.CSS_SELECTOR, product_name)
                    else:
                        name_match = driver.find_element(By.CSS_SELECTOR, product_name)

                    productname = name_match.text.strip()
                except NoSuchElementException:
                    productname = "Product name not found"
                print(productname)

                # for shade name
                try:
                    test = driver.find_element(By.CSS_SELECTOR, shade_name)
                    selected_shade_text = test.text.strip()
                    print(selected_shade_text)
                except NoSuchElementException:
                    selected_shade_text = "Shade name not found"
                    print(selected_shade_text)

                # for image
                try:
                    if shade_image_srcset:
                        test1 = driver.find_element(By.XPATH, shade_image_srcset)
                        data = test1.get_attribute('srcset')
                        data = data.replace('//', '')
                    elif shade_image_src:
                        test1 = driver.find_element(By.XPATH, shade_image_src)
                        data = test1.get_attribute('src')
                    else:
                        # Check if the image tag is present and get the srcset attribute if available
                        parent_img = driver.find_element(By.CSS_SELECTOR, img_parent)
                        image_tag = parent_img.find_element(By.CSS_SELECTOR, img_tag)
                        data = image_tag.get_attribute('srcset') if image_tag else None
                        data = data.replace('//', '')
                    if data.startswith('/'):
                        full_image_url = image_base_url + data
                    else:
                        full_image_url = data.split()[0] if data else "Image URL not available"
                    print(full_image_url)
                except NoSuchElementException:
                    full_image_url = "Image URL not available"
                    print(full_image_url)

                if "combo" not in selected_shade_text.lower():
                    shade_data = {
                        "shade_url": window_location,
                        "shade_image_url": full_image_url,
                        "shade_price": price,
                        "Product_Name": productname,
                        "original_price": oprice,
                        "Selected_shade_name": selected_shade_text,
                        "vendor": vendor
                    }

                    product_data["shades"].append(shade_data)

            return product_data

        finally:
            driver.quit()

    with open(f"{filename_prefix}_links.json", 'r') as f:
        links_data = json.load(f)

    links = links_data['links']

    for url in links:
        print(f"Scraping data from: {url}")
        scraped_data = scrape_data(url)
        all_data.append(scraped_data)
        print("-" * 50)

    # Define the output JSON file for this website based on the filename
    output_file = os.path.join(output_directory, f"{website_name}.json")

    with open(output_file, 'w') as f:
        json.dump(all_data, f, indent=4)

    print(f"Scraped data for {website_name} saved to '{output_file}'")

print(f"Scraped data saved in directory '{output_directory}'")
