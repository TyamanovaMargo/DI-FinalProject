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
from selenium_stealth import stealth
import pandas as pd
import os
import glob


def init_driver():
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome()

    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    return driver

driver = init_driver()




def smart_scroll(driver, pause_time=1):
        last_height = driver.execute_script("return document.body.scrollHeight")  # Сколько сейчас вся страница в пикселях

        while True:
            # Прокручиваем вниз до конца
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Ждём, чтобы страница успела подгрузить новые объявления
            time.sleep(pause_time)

            # Проверяем новую высоту страницы
            new_height = driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                # Если страница больше не увеличивается — значит всё загружено
                break

            last_height = new_height

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
        
def get_listings(driver):
        listings = driver.find_elements(By.CSS_SELECTOR, "li[data-testid='item-basic'][data-nagish='feed-item-list-box']")
        return listings

# Create an empty list for all ads
data = []

for page_number in range(60, 90):  # от 1 до 10 страницы
    url = f"https://www.yad2.co.il/realestate/forsale?page={page_number}"
    driver.get(url)
    time.sleep(2)  # Wait for the page to load

    # Wait for listings to load
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "li[data-testid='item-basic'][data-nagish='feed-item-list-box']"))

    )
 

    smart_scroll(driver)
    listings = get_listings(driver)  # Get all listings on the current page
    print(f"Found {len(listings)} listings")

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
        try:
            tags_div = WebDriverWait(listing, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[class^='item-tags_itemTagsBox']"))
            )
            span_tags = tags_div.find_elements(By.TAG_NAME, "span")
            tags_adiitional_info = [span.text.strip() for span in span_tags]
            info1 = tags_adiitional_info[0] if len(tags_adiitional_info) > 0 else None
            info2 = tags_adiitional_info[1] if len(tags_adiitional_info) > 1 else None
            info3 = tags_adiitional_info[2] if len(tags_adiitional_info) > 2 else None
        except Exception as e:
            info1 = info2 = info3 = None
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
        # pause for a bit to avoid being blocked
        # time.sleep(5)



# Превращаем список в pandas DataFrame
df = pd.DataFrame(data)

# Сохраняем в CSV
output_folder = "/Users/margotiamanova/Desktop/DI-FinalProject/results/raw_results"  # замените на ваш путь
output_filename = "yad2_listings_4.csv"
output_path = os.path.join(output_folder, output_filename)
df.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f" CSV saved as {output_path}")
# Close browser
driver.quit()
