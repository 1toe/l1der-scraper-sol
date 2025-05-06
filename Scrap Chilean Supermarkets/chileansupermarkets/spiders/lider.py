from datetime import date
import scrapy
import json
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def clean_sku_from_url(url):
    match = re.search(r'/sku/(\d+)/', url)
    return match.group(1) if match else None

def parse_numeric(value):
    try:
        return float(''.join(filter(lambda x: x.isdigit() or x == '.', value)))
    except:
        return None

class LiderSpider(scrapy.Spider):
    name = "lider"
    allowed_domains = ["lider.cl"]
    start_urls = ["https://www.lider.cl/supermercado/category/Despensa/Arroz-y-Legumbres/Arroz/"]
    
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 5,
        'COOKIES_ENABLED': True,
        'FEEDS': {
            'lider_products_full.json': {
                'format': 'json',
                'encoding': 'utf8',
                'indent': 4,
            },
        }
    }

    def __init__(self):
        options = uc.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')
        self.driver = uc.Chrome(options=options)
        super().__init__()

    def closed(self, reason):
        if hasattr(self, 'driver'):
            self.driver.quit()

    def wait_for_element(self, selector, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )

    def parse_product_selenium(self, response):
        url = response.url
        self.driver.get(url)
        time.sleep(5)  # Esperar a que cargue la página

        try:
            # Buscar elementos usando los nuevos selectores
            ingredients = None
            allergens = None
            nutritional_info = {}

            try:
                ingredients_div = self.driver.find_element(By.CSS_SELECTOR, 'div:contains("Ingredientes:")')
                if ingredients_div:
                    ingredients = ingredients_div.find_element(By.XPATH, 'following-sibling::div').text
            except:
                self.logger.warning(f"No se encontraron ingredientes para {url}")

            try:
                allergens_div = self.driver.find_element(By.CSS_SELECTOR, 'div:contains("Declaración de Alérgenos:")')
                if allergens_div:
                    allergens = allergens_div.find_element(By.XPATH, 'following-sibling::div').text
            except:
                self.logger.warning(f"No se encontraron alérgenos para {url}")

            try:
                # Buscar tabla nutricional
                table = self.driver.find_element(By.CSS_SELECTOR, 'table')
                rows = table.find_elements(By.TAG_NAME, 'tr')
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, 'td')
                    if len(cells) >= 2:
                        key = cells[0].text.strip()
                        value = parse_numeric(cells[1].text)
                        nutritional_info[key] = value
            except:
                self.logger.warning(f"No se encontró tabla nutricional para {url}")

            # Obtener información del JSON-LD
            scripts = self.driver.find_elements(By.CSS_SELECTOR, 'script[type="application/ld+json"]')
            product_data = None
            for script in scripts:
                try:
                    data = json.loads(script.get_attribute('innerHTML'))
                    if isinstance(data, dict) and data.get('@type') == 'Product':
                        product_data = data
                        break
                except:
                    continue

            if product_data:
                return {
                    'name': product_data.get('name'),
                    'brand': product_data.get('brand', {}).get('name'),
                    'sku': clean_sku_from_url(url),
                    'price': product_data.get('offers', {}).get('price'),
                    'url': url,
                    'ingredients': ingredients,
                    'allergens': allergens,
                    'nutritional_info': nutritional_info,
                    'extraction_date': str(date.today())
                }

        except Exception as e:
            self.logger.error(f'Error extrayendo datos del producto {url}: {str(e)}')
            return None

    def parse_category_selenium(self):
        try:
            # Esperar a que el script con JSON-LD esté presente
            script = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'script[type="application/ld+json"]'))
            )
            
            # Extraer los datos del JSON-LD
            data = json.loads(script.get_attribute('innerHTML'))
            if isinstance(data, dict) and data.get('@type') == 'ItemList':
                items = data.get('itemListElement', [])
                urls = []
                for item in items:
                    product = item.get('item', {})
                    product_url = product.get('url')
                    if product_url:
                        urls.append(product_url)
                return urls
        except Exception as e:
            self.logger.error(f'Error extrayendo URLs de productos: {str(e)}')
            return []

    def start_requests(self):
        self.driver.get(self.start_urls[0])
        time.sleep(5)  # Esperar a que cargue la página

        # Extraer URLs de productos del JSON-LD
        urls = self.parse_category_selenium()
        
        if not urls:
            self.logger.error('No se encontraron URLs de productos')
            return

        for url in urls:
            yield scrapy.Request(url, 
                              callback=self.parse_product,
                              dont_filter=True,
                              meta={'selenium': True})

    def parse_product(self, response):
        if response.meta.get('selenium'):
            product_data = self.parse_product_selenium(response)
            if product_data:
                yield product_data
