import json

import boto3 as boto3
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
import os  # Import the os module
from datetime import date
import traceback
from concurrent.futures import ThreadPoolExecutor, wait

# Chrome options to run headless
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")

# Set the viewport size
chrome_options.add_argument("--window-size=1920,1080")

# Path to ChromeDriver executable
chrome_driver_path = '/usr/bin/chromedriver'

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


def scrape_data(url):
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    try:
        driver.implicitly_wait(10)
        shade_items = driver.find_elements(By.CSS_SELECTOR, '.css-11ozycd')
        product_counter = 0
        brand_name_found = False
        product_data = {
            "url": url,
            "shades": [],
            "brand_name": ""

        }

        for shade_item in shade_items:
            driver.implicitly_wait(10)
            product_counter += 1
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

            try:
                price_match = driver.find_element(By.CSS_SELECTOR, '.css-1jczs19')
                price = price_match.text.strip()
                print(price)
            except NoSuchElementException:
                price = "Price not found"
                print(price)

            try:
                original_price_match = driver.find_element(By.CSS_SELECTOR, '.css-u05rr')
                original_price = original_price_match.text.strip()
                print(original_price)
            except NoSuchElementException:
                original_price = "Price not found"
                print(original_price)

            result = None

            try:
                name_match = driver.find_element(By.CSS_SELECTOR, '.css-1gc4x7i')
                pname = name_match.text.strip()

                # Remove everything after the hyphen '-'
                pname = pname.split('-')[0].strip()

                print(pname)

                keywords = ['satin', 'metallic', 'matte', 'gloss']
                found_keywords = [keyword for keyword in keywords if keyword in pname.lower()]

                if found_keywords:
                    result = found_keywords[0]
                    print(result)
                else:
                    result = ""
                    print(result)

            except NoSuchElementException:
                pname = "Product name not found"
                print(pname)

            try:
                test = driver.find_element(By.CSS_SELECTOR, '.active.css-10ht89k')
                shade_name = test.find_element(By.TAG_NAME, 'img')
                selected_shade_text = shade_name.get_attribute('alt')
                selected_shade_name = selected_shade_text.replace('Color:', '').strip()
                print(selected_shade_name)
            except NoSuchElementException:
                try:
                    test = driver.find_element(By.CSS_SELECTOR, '.oos.css-10ht89k')
                    shade_name = test.find_element(By.TAG_NAME, 'img')
                    selected_shade_text = shade_name.get_attribute('alt')
                    selected_shade_name = selected_shade_text.replace('Color:', '').strip()
                except NoSuchElementException:
                    selected_shade_name = "Shade name not found"
                    print(selected_shade_name)

            try:
                color_code_img = driver.find_element(By.CSS_SELECTOR, '.active.css-10ht89k')
                shade_name = color_code_img.find_element(By.TAG_NAME, 'img')
                color_code = shade_name.get_attribute('src')
                background_color_rgb = get_image_rgb(color_code)
                print(background_color_rgb)
            except NoSuchElementException:
                try:
                    color_code_img = driver.find_element(By.CSS_SELECTOR, '.active.css-10ht89k')
                    shade_name = color_code_img.find_element(By.TAG_NAME, 'img')
                    color_code = shade_name.get_attribute('src')
                    background_color_rgb = get_image_rgb(color_code)
                    print(background_color_rgb)
                except NoSuchElementException:
                    background_color_rgb = "color code not found"
                    print(background_color_rgb)

            try:
                test1 = driver.find_element(By.CSS_SELECTOR,
                                            '#app > div.css-e82s8r > div.css-16kpx0l > div.css-14y2xde > div.css-1mruek6 > div.css-ov1ktg > div.productSelectedImage.css-eyk94w > div > div > img')
                data = test1.get_attribute('src')
                # data = data.replace('//', '')
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
                "Product_type": result,
                "Selected_shade_name": selected_shade_name,
                "vendor": "Nykaa E-Retail Pvt. Ltd"
            }

            product_data["shades"].append(shade_data)

            # Wait for the element to be clickable
        btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.css-1eymbsg'))
            )
        driver.execute_script("arguments[0].scrollIntoView();", btn)



        # Click the element
        driver.execute_script("arguments[0].click();", btn)

        elements = driver.find_elements(By.CSS_SELECTOR, '.content-info')
        # Check if there is a second element
        if len(elements) >= 2:
            # Get the text of the second element
            name = elements[1].text.strip()
            print(name)
            product_data['brand_name'] = name

        else:
            print("There is no second element with class name .content-info")

        return product_data

    except Exception as e:
        print(f"An error occurred while scraping the URL: {url}")
        print(f"Error: {str(e)}")
        with open(log_file_path, 'a') as log_file:
            log_file.write(f"An error occurred while scraping the URL: {url}\n")
            log_file.write(f"Error: {str(e)}\n")
            traceback.print_exc()

    finally:
        driver.quit()
def scrape_data_with_threading(links):
    all_data = []

    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit scraping tasks for each URL
        scraping_tasks = {executor.submit(scrape_data, url): url for url in links}

        # Wait for all tasks to complete
        wait(scraping_tasks)

        # Retrieve results from completed tasks
        all_data = [result.result() for result in scraping_tasks if result.result() is not None]

    return all_data

processed_urls = set()

# Load links from JSON file
with open('links.json', 'r') as f:
    links_data = json.load(f)

links = links_data['links']

# scrape_data_with_threading(links)

all_data = []

for url in links:
    if url in processed_urls:
        print(f"URL {url} already processed. Skipping.")
        continue
     
    print(f"Scraping data from: {url}")
    scraped_data = scrape_data_with_threading(links)
    if scraped_data:
        # Append the scraped data for this URL to the list
        all_data.append(scraped_data)

        # Save the updated data to the JSON file after scraping each URL
        output_file_partial = os.path.join(output_directory, 'partial_scraped_data.json')
        with open(output_file_partial, 'w') as f:
            json.dump(all_data, f, indent=4)
            print(f"Partial scraped data saved to '{output_file_partial}'")
        # Mark the URL as processed
        processed_urls.add(url)

    print("-" * 50)

# Exclude shades with "combo" keyword
all_data_filtered = []
for data in all_data:
    shades_filtered = [shade for shade in data["shades"] if "combo" not in shade["Selected_shade_name"].lower()]
    if shades_filtered:
        data["shades"] = shades_filtered
        all_data_filtered.append(data)

# Save all scraped data to a single JSON file
output_file_final = os.path.join(output_directory, 'all_scraped_data.json')
with open(output_file_final, 'w') as f:
    json.dump(all_data, f, indent=4)

print(f"All scraped data saved to '{output_file_final}'")

# Calculate the total count of shades
total_shade_count = sum(len(data["shades"]) for data in all_data_filtered)

# Print the total count of shades to the console
print(f"Total count of shades: {total_shade_count}")

# Log the total count of shades
with open(log_file_path, 'a') as log_file:
    log_file.write(f"Total count of shades: {total_shade_count}\n")
# AWS credentials and S3 bucket information
aws_access_key_id = 'AKIA5LN5QZFXC7TK5BXL'
aws_secret_access_key = '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'
brand_name = "nykaa"
bucket_name = 'dataset-image-dev'
s3_prefix = 'web_scrape_data/{}/{}/lipstick/'.format(current_date, brand_name)
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
