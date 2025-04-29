import time
import csv
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = uc.ChromeOptions()
driver = uc.Chrome(options=options)

base_url = "https://www.yad2.co.il/realestate/forsale?page="

# How many pages you want to scrape
NUM_PAGES = 100

results = []

try:
    for page in range(1, NUM_PAGES + 1):
        print(f"\n🌐 Scraping page {page}...")

        driver.get(base_url + str(page))
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "item-layout_feedItemBox__Kvh1y"))
        )
        time.sleep(2)

        cards = driver.find_elements(By.CLASS_NAME, "item-layout_feedItemBox__Kvh1y")
        print(f"🔍 Found {len(cards)} cards")

        for card in cards:
            try:
                price = card.find_element(By.CLASS_NAME, "feed-item-price_price__ygoeF").text.strip()
                link = card.find_element(By.CLASS_NAME, "item-layout_itemLink__CZZ7w").get_attribute("href")
                full_link = "https://www.yad2.co.il" + link if link.startswith("/") else link

                print(f"💰 Price: {price} | 🔗 Link: {full_link}")
                results.append((price, full_link))
            except Exception as e:
                try:
                    fallback_link = card.find_element(By.CLASS_NAME, "item-layout_itemLink__CZZ7w").get_attribute("href")
                    full_fallback_link = "https://www.yad2.co.il" + fallback_link if fallback_link.startswith("/") else fallback_link
                    print(f"⚠️ Failed card URL: {full_fallback_link}")
                except:
                    print("⚠️ Failed to extract link from bad card too.")
                print("⚠️ Error parsing card:", e)

finally:
    driver.quit()

# Save all results
with open("yad2_prices.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["Price", "Link"])
    writer.writerows(results)

print("\n✅ Finished scraping and saved to yad2_prices.csv")
