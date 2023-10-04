import json
import requests
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, \
    ElementNotInteractableException, ElementClickInterceptedException
from bs4 import BeautifulSoup
import time
from PIL import Image
import boto3
import traceback

import os  # Import the os module
from datetime import date

# Get the current date in the format "dd-mm-yyyy"
current_date = date.today().strftime("%d-%m-%Y")

# Create a folder with the current date if it doesn't exist
folder_name = os.path.join(os.getcwd(), current_date)
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Define the local directory containing the files to upload
output_directory = folder_name

# Define the log file path
log_file_path = os.path.join(output_directory, 'scraping_log.txt')

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
chrome_driver_path = '/usr/bin/chromedriver'

# Initialize counters
total_product_count = 0
website_product_counts = {}

def get_image_rgb(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
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

# Initialize a dictionary to store data for each website
data_by_website = {}

for target in scraping_targets:
    filename_prefix = target["filename"]
    # Check if the website is already in the dictionary
    if filename_prefix not in data_by_website:
        data_by_website[filename_prefix] = []

    product_name = target["product_name"]
    shade_image_srcset = target["shade_image_srcset"]
    shade_click = target["shade_click"]
    shade_Original_Price = target['shade_Original_Price']
    shade_price = target['shade_price']
    shade_name_tag = target['shade_name_tag']
    image_base_url = target['image_base_url']
    vendor = target['vendor']
    shade_image_src = target["shade_image_src"]
    parent_element = target['parent_element']
    product_name_parent = target['product_name_parent']
    price_parent = target['price_parent']
    img_tag = target['img_tag']
    img_parent = target['img_parent']
    shade_details_parent = target['shade_details_parent']

    # Load links from JSON file
    with open(f"{filename_prefix}.json", 'r') as f:
        links_data = json.load(f)

    links = links_data['links']

    # Count the shades for each website
    total_shades_count = 0

    # Store the scraped data for a website
    website_data = {
        "website_name": filename_prefix,
        "shades": []
    }

    for url in links:
        print(f"Scraping data from: {url}")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        try:
            driver.implicitly_wait(10)
            try:
                if parent_element:
                    parent = driver.find_element(By.CSS_SELECTOR, parent_element)
                    shade_items = parent.find_elements(By.CSS_SELECTOR, shade_click)
                else:
                    shade_items = driver.find_elements(By.CSS_SELECTOR, shade_click)
            except NoSuchElementException:
                print("No Such Element")
                continue

            product_counter = 0

            for shade_item in shade_items:
                driver.implicitly_wait(10)
                product_counter += 1
                total_shades_count += 1  # Increment the total shades count for this website
                print(f"Product #{product_counter}")

                try:
                    shade_item.click()
                except ElementNotInteractableException:
                    print("Could not click on the shade item (OUT OF STOCK). Skipping to the next one.")
                except ElementClickInterceptedException:
                    print("Element is click-intercepted, waiting for a second and trying again.")
                    time.sleep(1)  # Wait for a second
                    try:
                        shade_item.click()  # Attempt to click again after waiting
                    except (ElementNotInteractableException, ElementClickInterceptedException):
                        print("Still unable to click on the shade item. Skipping to the next one.")

                # time.sleep(3)
                window_location = driver.execute_script("return window.location.href")
                print(window_location)
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')

                # saleprice
                try:
                    price_match = driver.find_element(By.CSS_SELECTOR, shade_price)
                    price = price_match.text.strip()
                    print(price)
                except NoSuchElementException:
                    price = "Price not found"
                    print(price)

                # originalprice
                try:
                    original_price_match = driver.find_element(By.CSS_SELECTOR, shade_Original_Price)
                    original_price = original_price_match.text.strip()
                    print(original_price)
                except NoSuchElementException:
                    original_price = "Price not found"
                    print(original_price)

                # for product name
                result = None
                try:
                    name_match = driver.find_element(By.CSS_SELECTOR, product_name)
                    pname = name_match.text.strip()
                    print(pname)
                    keywords = ['satin', 'metallic', 'matte', 'gloss']
                    # Iterate through keywords and check if they are in the product name
                    found_keywords = [keyword for keyword in keywords if keyword in pname.lower()]
                    if found_keywords:
                        # Print the first found keyword
                        result = found_keywords[0]
                        print(result)
                    else:
                        result = "N/A"
                        print(result)
                except NoSuchElementException:
                    pname = "Product name not found"
                    print(pname)

                # shadename
                try:
                    test = driver.find_element(By.CSS_SELECTOR, shade_details_parent)
                    shade_name = test.find_element(By.TAG_NAME, shade_name_tag)
                    selected_shade_text = shade_name.get_attribute('alt')
                    selected_shade_name = selected_shade_text.replace('Color:', '').strip()
                    print(selected_shade_name)

                except NoSuchElementException:
                    selected_shade_name = "Shade name not found"
                    print(selected_shade_name)

                # shadecolor
                try:
                    color_code_img = driver.find_element(By.CSS_SELECTOR, shade_details_parent)
                    shade_name = color_code_img.find_element(By.TAG_NAME, shade_name_tag)
                    color_code = shade_name.get_attribute('src')
                    background_color_rgb = get_image_rgb(color_code)
                    print(background_color_rgb)

                except NoSuchElementException:
                    background_color_rgb = "color code not found"
                    print(background_color_rgb)

                # productimage
                try:
                    test1 = driver.find_element(By.CSS_SELECTOR,
                                                '#app > div.css-e82s8r > div.css-16kpx0l > div.css-14y2xde > div.css-1mruek6 > div.css-ov1ktg > div.productSelectedImage.css-eyk94w > div > div > img')
                    data = test1.get_attribute('src')
                    data = data.replace('//', '')
                    full_image_url = data.split()[0] if data else "Image URL not available"
                    print(full_image_url)
                except NoSuchElementException:
                    full_image_url = "Image URL not available"
                    print(full_image_url)

                shade_data = {
                    "shade_url": window_location,
                    "shade_color": background_color_rgb,
                    "shade_image_url": full_image_url,
                    "shade_sale_price": price,
                    "shade_original_price": original_price,
                    "Product_Name": pname,
                    "product_type": result,
                    "Selected_shade_name": selected_shade_name,
                    "vendor": vendor
                }

                # Append the scraped data to the website's data
                website_data["shades"].append(shade_data)

            # Print the total count of shades for this website
            print(f"Total shades for {filename_prefix}: {total_shades_count}")

            # Update the total product count and website product count
            total_product_count += total_shades_count
            website_product_counts[filename_prefix] = total_shades_count

        except Exception as e:
            print(f"An error occurred while scraping the URL: {url}")
            print(f"Error: {str(e)}")
            with open(log_file_path, 'a') as log_file:
                log_file.write(f"An error occurred while scraping the URL: {url}\n")
                log_file.write(f"Error: {str(e)}\n")
                traceback.print_exc()
            # If an error occurs, continue to indicate that the scraping failed for this URL
            continue

        finally:
            driver.quit()

    # Save scraped data for this website to a JSON file
    output_file = os.path.join(output_directory, f"{filename_prefix}.json")
    with open(output_file, 'w') as f:
        json.dump(website_data, f, indent=4)
    print(f"Scraped data for {filename_prefix} saved to '{output_file}'")

# Print the total count of shades across all websites
print(f"Total shades across all websites: {total_product_count}")


# Print the counts for each website
for website, count in website_product_counts.items():
    print(f"Total shades for {website}: {count}")

print(f"Scraped data saved in directory '{output_directory}'")


# AWS credentials and S3 bucket information
aws_access_key_id = 'AKIA5LN5QZFXC7TK5BXL'
aws_secret_access_key = '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'
bucket_name = 'dataset-image-dev'
s3_prefix = 'web_scrape_data/' + current_date + '/' + 'nykaa_Setup' + '/'

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

