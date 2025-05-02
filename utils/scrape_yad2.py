# scrape_yad2.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import time
import pandas as pd
import os
import re

def init_driver(headless=True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)

    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    return driver

def smart_scroll(driver, pause_time=1):
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def extract_count(text, parameter):
    patterns = {
        1: r'(\d+)\s+חדרים',
        2: r'קומה\s+(\d+)',
        3: r'(\d+)\s+מ״ר'
    }
    if parameter in patterns:
        match = re.search(patterns[parameter], text)
        return match.group(1) if match else None
    return None

def get_listings(driver):
    return driver.find_elements(By.CLASS_NAME, "item-layout_feedItemBox__Kvh1y")

def scrape_yad2_pages(start_page=1, end_page=3, output_folder='.', output_filename="yad2_listings.csv"):
    driver = init_driver()
    data = []

    try:
        for page_number in range(start_page, end_page + 1):
            url = f"https://www.yad2.co.il/realestate/forsale?page={page_number}"
            driver.get(url)
            time.sleep(2)

            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "item-layout_feedItemBox__Kvh1y"))
            )

            smart_scroll(driver)
            listings = get_listings(driver)
            print(f"Page {page_number}: Found {len(listings)} listings")

            for listing in listings:
                try:
                    address = listing.find_element(By.CLASS_NAME, "item-data-content_heading__tphH4").text
                except:
                    address = None

                try:
                    price_text = listing.find_element(By.CLASS_NAME, "item-data-content_priceSlot__yzYXU").text
                    price_text = price_text.replace("₪", "NIS").strip()
                    currency, number_str = price_text.split(" ", 1)
                    price_number = int(number_str.replace(",", ""))
                except:
                    price_number = currency = None

                try:
                    link = listing.find_element(By.CLASS_NAME, "item-layout_itemLink__CZZ7w").get_attribute("href")
                except:
                    link = None

                try:
                    content = listing.find_element(By.XPATH, './/h2[@data-nagish="content-section-title"]').text
                    parts = content.split('•')
                    area_size = extract_count(parts[-1].strip(), 3)
                    floor_count = extract_count(parts[-2].strip(), 2)
                    rooms_count = extract_count(parts[-3].strip(), 1)
                except:
                    area_size = floor_count = rooms_count = None

                try:
                    info_line = listing.find_element(By.XPATH, './/span[contains(@class, "item-data-content_itemInfoLine__AeoPP")]').text
                    parts = info_line.split(',')
                    property_type = parts[0].strip() if len(parts) > 0 else None
                    neighborhood = parts[1].strip() if len(parts) > 1 else None
                    city = parts[2].strip() if len(parts) > 2 else None
                except:
                    property_type = neighborhood = city = None

                try:
                    tags_div = WebDriverWait(listing, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[class^='item-tags_itemTagsBox']"))
                    )
                    span_tags = tags_div.find_elements(By.TAG_NAME, "span")
                    tags = [span.text.strip() for span in span_tags]
                    info1 = tags[0] if len(tags) > 0 else None
                    info2 = tags[1] if len(tags) > 1 else None
                    info3 = tags[2] if len(tags) > 2 else None
                except:
                    info1 = info2 = info3 = None

                data.append({
                    "Address": address,
                    "Price": price_number,
                    "Currency": currency,
                    "Link": link,
                    "Property Type": property_type,
                    "Rooms_count": rooms_count,
                    "Floor": floor_count,
                    "Area": area_size,
                    "City": city,
                    "Neighborhood": neighborhood,
                    "Tags1": info1,
                    "Tags2": info2,
                    "Tags3": info3,
                })
    finally:
        driver.quit()

    # Save to CSV
    df = pd.DataFrame(data)
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, output_filename)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f" CSV saved as: {output_path}")
