import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
from baomoi_urls import urls

# Initialize the Chrome WebDriver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

# Function to scroll to the end of the page
def scroll_to_end_of_page(driver, scroll_pause_time=2):
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# Function to extract <h3> links from the page
def extract_h3_links_from_page(driver, category):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    base_url = driver.current_url

    h3_tags = soup.find_all('h3', class_='font-semibold block')
    extracted_data = []
    for h3 in h3_tags:
        a_tag = h3.find('a')
        if a_tag:
            href = a_tag.get('href')
            title = a_tag.get('title', '').strip()  # Use the title attribute if available
            text = a_tag.text.strip()  # Get the text inside the <a> tag

            if href:
                full_url = urljoin(base_url, href)  # Handle relative URLs
                extracted_data.append({'url': full_url, 'title': title or text, 'label': True, 'category': category})

    return extracted_data

# Function to crawl an infinite scroll page and extract data
def crawl_infinite_scroll(url, category, scroll_pause_time=2):
    driver.get(url)
    scroll_to_end_of_page(driver, scroll_pause_time)
    data = extract_h3_links_from_page(driver, category)
    return data

# Function to save the extracted data to a CSV file
def save_to_csv(data, file_name):
    if data:
        keys = data[0].keys()
        with open(file_name, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)

# Recursive function to handle nested dictionaries
def extract_data_from_urls(urls_dict):
    all_data = []
    for category, url_or_subdict in urls_dict.items():
        if isinstance(url_or_subdict, dict):
            # If there are subcategories, loop through them but keep the main category as the label
            for subcategory, url in url_or_subdict.items():
                print(f"Crawling subcategory: {subcategory} (under main category: {category}) - {url}")
                extracted_data = crawl_infinite_scroll(url, category)  # Use the main category as the label
                all_data.extend(extracted_data)
        else:
            # Crawl and extract data for the main category URL
            print(f"Crawling main category: {category} - {url_or_subdict}")
            extracted_data = crawl_infinite_scroll(url_or_subdict, category)
            all_data.extend(extracted_data)
    return all_data


# Extract data from all URLs
all_extracted_data = extract_data_from_urls(urls)

# Save the extracted data to a CSV file
save_to_csv(all_extracted_data, 'all.csv')

# Close the browser
driver.quit()
