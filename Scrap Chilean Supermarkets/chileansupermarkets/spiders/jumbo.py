from datetime import date
import scrapy
from scrapy import Request
import logging
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import random

class Jumbo(scrapy.Spider):
    name = "jumbo"
    allowed_domains = ["jumbo.cl"]
    start_urls = ["https://www.jumbo.cl/despensa"]
    
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 3,
        'COOKIES_ENABLED': True,
        'DOWNLOAD_TIMEOUT': 180,
        'RANDOMIZE_DOWNLOAD_DELAY': True
    }

    def __init__(self, *args, **kwargs):
        super(Jumbo, self).__init__(*args, **kwargs)
        options = uc.ChromeOptions()
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-automation')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Agregar user agent más reciente
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
        
        self.driver = uc.Chrome(options=options)
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'})
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def closed(self, reason):
        if hasattr(self, 'driver'):
            self.driver.quit()

    def random_delay(self):
        time.sleep(random.uniform(4, 8))
        
    def human_like_scroll(self):
        """Simula scroll humano"""
        total_height = self.driver.execute_script("return document.body.scrollHeight")
        viewport_height = self.driver.execute_script("return window.innerHeight")
        current_position = 0
        
        while current_position < total_height:
            scroll_amount = random.randint(100, 300)
            current_position += scroll_amount
            self.driver.execute_script(f"window.scrollTo(0, {current_position});")
            time.sleep(random.uniform(0.5, 1.5))

    def parse(self, response):
        """Método principal para procesar la página de listado de productos"""
        try:
            self.driver.get(response.url)
            self.random_delay()
            
            # Simular comportamiento humano
            self.human_like_scroll()
            
            # Esperar a que los productos sean visibles
            try:
                products = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-item, .shelf-product-island"))
                )
                
                self.logger.info(f"Encontrados {len(products)} productos")
                
                # Procesar cada producto encontrado
                for product in products:
                    try:
                        # Mover el mouse al producto para simular interacción humana
                        ActionChains(self.driver).move_to_element(product).perform()
                        time.sleep(random.uniform(0.2, 0.5))
                        
                        url = product.find_element(By.CSS_SELECTOR, "a[href*='/product/']").get_attribute("href")
                        name = product.find_element(By.CSS_SELECTOR, ".product-name, .shelf-product-title").text
                        self.logger.info(f"Procesando producto: {name}")
                        
                        yield Request(
                            url,
                            callback=self.parse_page,
                            meta={'url': url, 'name': name},
                            dont_filter=True
                        )
                    except Exception as e:
                        self.logger.error(f"Error al procesar producto en listado: {str(e)}")
                    
                # Intentar encontrar el botón de siguiente página
                try:
                    next_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, ".load-more-button, .shelf-see-more"))
                    )
                    if next_button and next_button.is_displayed():
                        ActionChains(self.driver).move_to_element(next_button).perform()
                        time.sleep(random.uniform(1, 2))
                        next_button.click()
                        self.random_delay()
                        yield Request(
                            self.driver.current_url,
                            callback=self.parse,
                            dont_filter=True
                        )
                except Exception as e:
                    self.logger.info("No hay más páginas para procesar")
                    
            except Exception as e:
                self.logger.error(f"Error esperando productos: {str(e)}")
                    
        except Exception as e:
            self.logger.error(f"Error al procesar la página de listado: {str(e)}")

    def parse_page(self, response):
        """Método para procesar la página de detalle del producto"""
        try:
            self.driver.get(response.url)
            self.random_delay()
            
            # Scroll suave por la página
            self.human_like_scroll()
            
            # Extraer datos del producto usando Selenium
            data = {
                "name": response.meta.get('name') or self.safe_extract(By.CSS_SELECTOR, "h1.product-name"),
                "sku": self.safe_extract(By.CSS_SELECTOR, "span.product-code, span.product-sku"),
                "price": self.safe_extract(By.CSS_SELECTOR, "span.active-price, span.sales-price"),
                "regular_price": self.safe_extract(By.CSS_SELECTOR, "span.regular-price, span.list-price"),
                "brand": self.safe_extract(By.CSS_SELECTOR, "div.brand-name, span.product-brand"),
                "category": self.safe_extract(By.CSS_SELECTOR, "span.breadcrumb-item, div.breadcrumb"),
                "description": self.safe_extract(By.CSS_SELECTOR, "div.product-description, div.product-details"),
                "extraction_date": str(date.today()),
                "url": response.url,
                "store": "jumbo",
                "stock_status": self.safe_extract(By.CSS_SELECTOR, "span.stock-status")
            }
            
            # Intentar obtener información nutricional
            try:
                nutrition_tab = self.driver.find_element(By.CSS_SELECTOR, "button[data-target='#nutrition-tab']")
                if nutrition_tab:
                    ActionChains(self.driver).move_to_element(nutrition_tab).perform()
                    time.sleep(random.uniform(0.5, 1))
                    nutrition_tab.click()
                    time.sleep(1)
                    data["nutritional_info"] = self.safe_extract(By.CSS_SELECTOR, "div.nutrition-info")
            except:
                pass
            
            # Limpiar valores None y espacios
            return {k: v.strip() if isinstance(v, str) else v 
                   for k, v in data.items() if v is not None}
                   
        except Exception as e:
            self.logger.error(f"Error al procesar producto {response.url}: {str(e)}")
    
    def safe_extract(self, by, selector, timeout=10):
        """Extrae texto de manera segura usando Selenium"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            return element.text
        except:
            return None