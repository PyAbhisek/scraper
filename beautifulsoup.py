import json
import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, \
    ElementNotInteractableException, ElementClickInterceptedException
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import os
from selenium.webdriver.common.action_chains import ActionChains
from datetime import date
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import boto3

# Load configuration from config.json
with open('BS4Config.json') as f:
    scraping_targets = json.load(f)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")

# Set the viewport size
chrome_options.add_argument("--window-size=1920,1080")

# Path to ChromeDriver executable
chrome_driver_path = '/usr/bin/google-chrome'


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
        click_element_safely(element)


# Handle popups for typsy
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


# Create a folder with today's date as the name
current_date = date.today().strftime("%d-%m-%Y")
folder_name = os.path.join(os.getcwd(), current_date)

if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Define the local directory containing the files to upload
output_directory = folder_name

# Iterate through the scraping targets
for target in scraping_targets:
    website_name = target["filename"]
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
    img_parent = target['img_parent']
    img_tag = target['img_tag']
    color_Code_tag = target['color_Code_tag']
    shade_image_classname = target['shade_image_classname']

    # Skip to the next JSON file if filename is not provided
    if not filename_prefix:
        print("Skipping to the next JSON file since filename is not provided.")
        continue

    # Construct the filename for the links JSON file
    links_filename = f"{filename_prefix}_links.json"

    # Check if the links JSON file exists before attempting to open it
    if not os.path.exists(links_filename):
        print(f"Links JSON file '{links_filename}' does not exist. Skipping to the next JSON file.")
        continue

    def scrape_data(url):
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        try:
            driver.implicitly_wait(10)
            product_counter = 0  # Initialize the product_counter
            trigger_popup_after = 2

            # Add a print statement to check if the URL is being opened correctly
            print(f"Opened URL: {url}")

            if parent_element:
                parent = driver.find_element(By.CSS_SELECTOR, parent_element)
                shade_items = parent.find_elements(By.CSS_SELECTOR, shade_click)
            else:
                shade_items = driver.find_elements(By.CSS_SELECTOR, shade_click)

            product_counter = 0

            product_data = {
                "url": url,
                "shades": []
            }

            for shade_item in shade_items:
                driver.implicitly_wait(10)
                product_counter += 1
                print(f"Product #{product_counter}")

                try:
                    shade_item.click()
                except (ElementNotInteractableException, ElementClickInterceptedException):
                    print("Could not click on the shade item (OUT OF STOCK). Skipping to the next one.")

                time.sleep(3)

                # link for the product
                window_location = driver.execute_script("return window.location.href")
                print(window_location)

                # for only typsy
                if filename_prefix == "typsybeauty" and product_counter == trigger_popup_after:
                    handle_popups(driver)

                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')

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

                # for shade price
                oprice = "Original Price not available"  # Default value

                if price_parent:
                    try:
                        parent_price = driver.find_element(By.CSS_SELECTOR, price_parent)
                        originalprice_match = parent_price.find_element(By.CSS_SELECTOR, shade_Original_Price)
                        oprice = originalprice_match.text.strip()
                    except NoSuchElementException:
                        pass  # Keep the default value

                elif shade_Original_Price:
                    try:
                        originalprice_match = driver.find_element(By.CSS_SELECTOR, shade_Original_Price)
                        oprice = originalprice_match.text.strip()
                    except NoSuchElementException:
                        pass  # Keep the default value

                print(oprice)

                # for product name
                try:
                    if product_name_parent:
                        product_name_parent_container = driver.find_element(By.CSS_SELECTOR, product_name_parent)
                        name_match = product_name_parent_container.find_element(By.CSS_SELECTOR, product_name)

                    else:
                        name_match = driver.find_element(By.CSS_SELECTOR, product_name)

                    productname = name_match.text.strip()
                    if not productname:
                        productname = name_match.get_attribute("textContent").strip()
                    if not productname:
                        productname = name_match.get_attribute("innerText").strip()

                except NoSuchElementException:
                    productname = "Product name not found"
                print(productname)

                # for shade
                try:
                    if shade_name:
                        test = driver.find_element(By.CSS_SELECTOR, shade_name)
                        selected_shade_text = test.text.strip()
                    else:
                        selected_shade_text = shade_item.text.strip()
                    print(selected_shade_text)
                except NoSuchElementException:
                    selected_shade_text = "Shade name not found"
                    print(selected_shade_text)

                # for color code
                rgb_color_Code = "color code not found"
                rgb_img_url = ""
                try:
                    if color_Code_tag:
                        color = shade_item.find_element(By.TAG_NAME, color_Code_tag)
                        rgb = color.get_attribute('style')

                    elif shade_item:
                        rgb = shade_item.get_attribute('style')

                    # Extract the RGB value from rgb_color_Code
                    start_index = rgb.find('(')
                    end_index = rgb.find(')')

                    if start_index != -1 and end_index != -1:
                        rgb_color_Code = rgb[start_index:end_index + 1]
                        print("rgb_color_Code:", rgb_color_Code)
                    else:
                        print("No RGB values found in style.")

                    # Check if 'background-image' is in rgb_color_Code and extract the URL
                    if 'background-image' in rgb:
                        start_index = rgb.index('url("') + len('url("')
                        end_index = rgb.index('")', start_index)
                        background_url = rgb[start_index:end_index]

                        # Check if background_url starts with "//"
                        if background_url.startswith('//'):
                            background_url = 'https:' + background_url

                        rgb_color_Code = get_image_rgb(background_url)
                    print(rgb_color_Code)

                except NoSuchElementException:
                    rgb_color_Code = "color code not found"
                    print(rgb_color_Code)

                # for image
                try:
                    if shade_image_srcset:
                        test1 = driver.find_element(By.XPATH, shade_image_srcset)
                        srcset = test1.get_attribute('srcset')
                        data = srcset.replace('//', '')
                    elif shade_image_src:
                        test1 = driver.find_element(By.XPATH, shade_image_src)
                        data = test1.get_attribute('src')
                    elif shade_image_classname:
                        img_class = driver.find_element(By.CSS_SELECTOR, shade_image_classname)
                        data = img_class.get_attribute('src')
                    else:
                        # Check if the image tag is present and get the srcset attribute if available
                        parent_img = driver.find_element(By.CSS_SELECTOR, img_parent)
                        image_tag = parent_img.find_element(By.CSS_SELECTOR, img_tag)
                        srcset = image_tag.get_attribute('srcset') if image_tag else None
                        data = srcset.replace('//', '')

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
                        "shade_color": rgb_color_Code,
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

    # Create a list to store data for the current website
    website_data = []

    for url in links:
        print(f"Scraping data from: {url}")
        scraped_data = scrape_data(url)
        website_data.append(scraped_data)
        print("-" * 50)

    # Define the output JSON file for this website based on the filename
    output_file = os.path.join(output_directory, f"{website_name}.json")

    # Write the data for the current website to the JSON file
    with open(output_file, 'w') as f:
        json.dump(website_data, f, indent=4)

    print(f"Scraped data for {website_name} saved to '{output_file}'")



print(f"Scraped data saved in directory '{output_directory}'")

# AWS credentials and S3 bucket information
aws_access_key_id = 'AKIA5LN5QZFXC7TK5BXL'
aws_secret_access_key = '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'
bucket_name = 'dataset-image-dev'
s3_prefix = 'web_scrape_data/' + current_date + '/'

# Create an S3 client
s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

# Iterate through the files in the output_directory and upload them to S3
for root, dirs, files in os.walk(output_directory):
    for file in files:
        local_path = os.path.join(root, file)
        # Define the S3 key (object name) by removing the local directory path
        s3_key = os.path.join(s3_prefix, os.path.relpath(local_path, output_directory))

        try:
            # Upload the file to S3
            s3.upload_file(local_path, bucket_name, s3_key)
            print(f"Uploaded {local_path} to s3://{bucket_name}/{s3_key}")
        except Exception as e:
            print(f"Error uploading {local_path} to s3://{bucket_name}/{s3_key}: {e}")

print(f"Scraped data in '{output_directory}' uploaded to S3 bucket '{bucket_name}' with prefix '{s3_prefix}'")
