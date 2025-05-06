import csv
import time
import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

def scroll_down(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def save_to_csv(scraped, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(['Supermarket', 'Name', 'Brand', 'Price', 'Reference Price', 'Date'])
        for data in scraped:
            csv_writer.writerow(['Lider', data['name'], data['brand'], data['price'], data['reference_price'], data['date']])
    print(f"Data saved to {filename}")

def scrape_lider(product):
    print(f'Starting scrape for {product}')
    now = datetime.datetime.now()
    date = now.strftime('%Y-%m-%d %H:%M')

    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = uc.Chrome(options=options)

    base_url = f"https://www.lider.cl/supermercado/search?query={product}&page=1"
    driver.get("https://www.lider.cl/")
    driver.get(base_url)
    print("Navigated to base URL")

    scraped = []
    page_number = 1
    while True:
        print(f"Scraping page {page_number}")
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.product-card')))
            scroll_down(driver)
            items = driver.find_elements(By.CSS_SELECTOR, '.product-card')
            if not items:
                print("No items found, check your class names.")
                break

            for item in items:
                try:
                    name = item.find_element(By.CSS_SELECTOR, '.product-card__name').text.strip()
                except Exception as e:
                    name = "Name not found"
                    print(f"Error finding name: {e}")
                
                try:
                    brand = item.find_element(By.CSS_SELECTOR, '.product-card__brand').text.strip()
                except Exception as e:
                    brand = "Brand not found"
                    print(f"Error finding brand: {e}")
                
                try:
                    price = item.find_element(By.CSS_SELECTOR, '.product-card__price--current').text.strip().replace('$', '').replace('.', '').strip()
                except Exception as e:
                    price = "Price not found"
                    print(f"Error finding price: {e}")
                
                try:
                    reference_price = item.find_element(By.CSS_SELECTOR, '.product-card__price--reference').text.strip().replace('$', '').replace('.', '').strip()
                except Exception as e:
                    reference_price = "No Reference Price"
                    print(f"Error finding reference price: {e}")
                
                if name != "Name not found":
                    scraped.append({
                        'brand': brand,
                        'name': name,
                        'price': price,
                        'reference_price': reference_price,
                        'date': date
                    })
                    print(f'Added {name} with price ${price} to list')

            page_number += 1
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, 'button.next')
                if next_button:
                    next_button.click()
                    time.sleep(2)
                else:
                    print("No next button found, stopping.")
                    break
            except Exception as e:
                print(f"Error clicking next button: {e}")
                break

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break

    driver.quit()
    return scraped

def run(product):
    scraped_data = scrape_lider(product)
    if scraped_data:
        filename = f'lider_{product}.csv'
        save_to_csv(scraped_data, filename)
    else:
        print(f"No data to save for {product}")

if __name__ == "__main__":
    product = "Perfumería y Salud/Cuidado Capilar"  # Example product category
    run(product)