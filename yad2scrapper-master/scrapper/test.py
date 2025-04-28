from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import time
import pandas as pd
import re

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # run in background
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Setup Chrome driver (make sure you have chromedriver installed)
# service = Service('/path/to/chromedriver')  # <<<--- REPLACE with your path
driver = webdriver.Chrome()

# Open the page
driver.get("https://www.yad2.co.il/realestate/forsale")

# Wait for listings to load
WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "li[data-testid='item-basic']"))
)

# Scroll to load more listings (optional)
for _ in range(3):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # wait for more items to load


def extract_count(parts, parameter):
   
    patterns = {
        1: r'(\d+)\s+חדרים',
        2: r'קומה\s+(\d+)',
        3: r'(\d+)\s+מ״ר'
    }
    
    if parameter in patterns:
        match = re.search(patterns[parameter], parts)
        if match:
            return match.group(1)
        else:
            return None
    else:
        return None
    

# Get listings
listings = driver.find_elements(By.CSS_SELECTOR, "li[data-testid='item-basic']")

# Create an empty list for all ads
data = []


for listing in listings:
    try:
        address = listing.find_element(By.CLASS_NAME, "item-data-content_heading__tphH4").text

    except:
        address = None

    try:
        price = listing.find_element(By.CLASS_NAME, "item-data-content_priceSlot__yzYXU").text
    except:
        price = None

    try:
        link_element = listing.find_element(By.CLASS_NAME, "item-layout_itemLink__CZZ7w")
        link = link_element.get_attribute("href")
    except:
        link = None
    try:
        content = listing.find_element(By.XPATH, './/h2[@data-nagish="content-section-title"]').text
        parts = content.split('•')
        # print(parts)
        area_parts = parts[-1].strip() 
        area_size = extract_count(area_parts,3)
        # print(area)   
        floor_parts = parts[-2].strip()
        floor_count = extract_count(floor_parts,2)

        rooms_parts = parts[-3].strip()
        rooms_count = extract_count(rooms_parts,1)
        
    except:
        link = None
    try:
        property_type = info = listing.find_element(By.XPATH, './/span[contains(@class, "item-data-content_itemInfoLine__AeoPP")]').text
        parts = property_type.split(',')
        property_type = parts[0].strip() if len(parts) > 0 else None
        neighborhood = parts[1].strip() if len(parts) > 1 else None
        city = parts[2].strip() if len(parts) > 2 else None
    except:
        link = None

    # print({
    #     "Title":address,
    #     "Price": price,
    #     "Link": link,
    #     "Content": content,
    #     "Property Type": property_type,
    #     "City": city,
    #     "Neighborhood": neighborhood
    # })
    # add to the list
    data.append({
        "Title": address,
        "Price": price,
        "Link": link,
        "Property Type": property_type,
        "Rooms_count": rooms_count,
        "Floor": floor_count,
        "Area": area_size,
        "City": city,
        "Neighborhood": neighborhood
    })



# Превращаем список в pandas DataFrame
df = pd.DataFrame(data)

# Сохраняем в CSV
df.to_csv('yad2_listings2.csv', index=False, encoding='utf-8-sig')

print("✅ CSV файл сохранен как yad2_listings2.csv")
# Close browser
driver.quit()
