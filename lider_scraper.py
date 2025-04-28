#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Lider Product Scraper

Este script extrae datos de productos del sitio web de Lider.cl, filtrando aquellos
que tienen máximo 2 sellos "ALTO EN" según la Ley 20.606.

Autor: Manus AI
Fecha: Abril 2025
"""

import time
import re
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager

class LiderScraper:
    """Clase para extraer datos de productos de Lider.cl con máximo 2 sellos 'ALTO EN'"""
    
    def __init__(self, headless=False, implicit_wait=10):
        """
        Inicializa el scraper de Lider
        
        Args:
            headless (bool): Si se ejecuta en modo headless (sin interfaz gráfica)
            implicit_wait (int): Tiempo de espera implícito en segundos
        """
        self.base_url = "https://www.lider.cl/supermercado"
        self.categories = []
        self.products = []
        
        # Configurar opciones de Chrome
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        
        # Configuraciones para evitar detección de bot
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        # Inicializar el driver
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.driver.implicitly_wait(implicit_wait)
        
        # Modificar el navigator.webdriver para evitar detección
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def login(self, email, password):
        """
        Inicia sesión en Lider.cl
        
        Args:
            email (str): Correo electrónico
            password (str): Contraseña
        
        Returns:
            bool: True si el inicio de sesión fue exitoso, False en caso contrario
        """
        try:
            self.driver.get(self.base_url)
            
            # Esperar a que se cargue la página y manejar posible captcha
            self._handle_captcha()
            
            # Hacer clic en el botón de inicio de sesión
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Ingresar')]"))
            )
            login_button.click()
            
            # Esperar a que aparezca el formulario de inicio de sesión
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            email_input.send_keys(email)
            
            password_input = self.driver.find_element(By.ID, "password")
            password_input.send_keys(password)
            
            # Hacer clic en el botón de inicio de sesión del formulario
            submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_button.click()
            
            # Esperar a que se complete el inicio de sesión
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Mi Cuenta')]"))
            )
            
            print("Inicio de sesión exitoso")
            return True
            
        except Exception as e:
            print(f"Error al iniciar sesión: {str(e)}")
            return False
    
    def _handle_captcha(self):
        """
        Maneja el captcha si aparece
        
        Returns:
            bool: True si se manejó correctamente, False en caso contrario
        """
        try:
            # Verificar si hay un captcha presente
            captcha_present = False
            try:
                captcha = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Persona o robot?')]"))
                )
                captcha_present = True
            except TimeoutException:
                return True  # No hay captcha
            
            if captcha_present:
                print("Captcha detectado. Se requiere intervención manual.")
                # Aquí se podría implementar una solución para resolver captchas automáticamente
                # o solicitar intervención manual
                
                # Esperar un tiempo para que el usuario resuelva el captcha manualmente
                time.sleep(30)
                
                # Verificar si se resolvió el captcha
                try:
                    WebDriverWait(self.driver, 5).until_not(
                        EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Persona o robot?')]"))
                    )
                    print("Captcha resuelto correctamente")
                    return True
                except TimeoutException:
                    print("El captcha no se resolvió correctamente")
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error al manejar el captcha: {str(e)}")
            return False
    
    def get_categories(self):
        """
        Obtiene las categorías de productos
        
        Returns:
            list: Lista de categorías
        """
        try:
            self.driver.get(self.base_url)
            
            # Manejar posible captcha
            self._handle_captcha()
            
            # Hacer clic en el botón de categorías
            categories_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Categorías')]"))
            )
            categories_button.click()
            
            # Esperar a que se carguen las categorías
            category_elements = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.category-item"))
            )
            
            # Extraer información de las categorías
            self.categories = []
            for element in category_elements:
                try:
                    category = {
                        'name': element.text.strip(),
                        'url': element.get_attribute('href')
                    }
                    self.categories.append(category)
                except StaleElementReferenceException:
                    continue
            
            print(f"Se encontraron {len(self.categories)} categorías")
            return self.categories
            
        except Exception as e:
            print(f"Error al obtener categorías: {str(e)}")
            return []
    
    def get_products_from_category(self, category_url, max_pages=3):
        """
        Obtiene los productos de una categoría
        
        Args:
            category_url (str): URL de la categoría
            max_pages (int): Número máximo de páginas a recorrer
        
        Returns:
            list: Lista de productos
        """
        try:
            self.driver.get(category_url)
            
            # Manejar posible captcha
            self._handle_captcha()
            
            category_products = []
            current_page = 1
            
            while current_page <= max_pages:
                # Esperar a que se carguen los productos
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.product-card"))
                )
                
                # Dar tiempo para que se carguen completamente los productos
                time.sleep(3)
                
                # Obtener los elementos de productos
                product_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.product-card")
                
                # Extraer información de los productos
                for element in product_elements:
                    try:
                        # Obtener URL del producto
                        product_link = element.find_element(By.CSS_SELECTOR, "a").get_attribute('href')
                        
                        # Obtener nombre del producto
                        product_name = element.find_element(By.CSS_SELECTOR, "h3.product-title").text.strip()
                        
                        # Obtener precio del producto
                        try:
                            product_price = element.find_element(By.CSS_SELECTOR, "span.price").text.strip()
                        except NoSuchElementException:
                            product_price = "Precio no disponible"
                        
                        # Obtener marca del producto
                        try:
                            product_brand = element.find_element(By.CSS_SELECTOR, "span.brand").text.strip()
                        except NoSuchElementException:
                            product_brand = "Marca no disponible"
                        
                        # Crear objeto de producto
                        product = {
                            'name': product_name,
                            'brand': product_brand,
                            'price': product_price,
                            'url': product_link,
                            'category': category_url.split('/')[-1]
                        }
                        
                        category_products.append(product)
                        
                    except StaleElementReferenceException:
                        continue
                    except Exception as e:
                        print(f"Error al procesar producto: {str(e)}")
                
                # Verificar si hay más páginas
                try:
                    next_button = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Next page')]")
                    if next_button.is_enabled():
                        next_button.click()
                        current_page += 1
                        time.sleep(3)  # Esperar a que se cargue la siguiente página
                    else:
                        break
                except NoSuchElementException:
                    break
            
            print(f"Se encontraron {len(category_products)} productos en la categoría")
            return category_products
            
        except Exception as e:
            print(f"Error al obtener productos de la categoría: {str(e)}")
            return []
    
    def get_product_details(self, product_url):
        """
        Obtiene los detalles de un producto
        
        Args:
            product_url (str): URL del producto
        
        Returns:
            dict: Detalles del producto
        """
        try:
            self.driver.get(product_url)
            
            # Manejar posible captcha
            self._handle_captcha()
            
            # Esperar a que se cargue la página del producto
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.product-detail"))
            )
            
            # Dar tiempo para que se carguen completamente los detalles
            time.sleep(3)
            
            # Obtener información básica del producto
            product_name = self.driver.find_element(By.CSS_SELECTOR, "h1.product-name").text.strip()
            
            try:
                product_brand = self.driver.find_element(By.CSS_SELECTOR, "span.brand").text.strip()
            except NoSuchElementException:
                product_brand = "Marca no disponible"
            
            try:
                product_price = self.driver.find_element(By.CSS_SELECTOR, "span.price").text.strip()
            except NoSuchElementException:
                product_price = "Precio no disponible"
            
            # Obtener sellos "ALTO EN"
            sellos_alto_en = []
            try:
                sellos_section = self.driver.find_element(By.XPATH, "//p[contains(text(), 'Sellos \"ALTO EN\"')]/following-sibling::p")
                sellos_text = sellos_section.text.strip()
                
                # Identificar los sellos presentes
                if "AZÚCARES" in sellos_text or "AZUCARES" in sellos_text:
                    sellos_alto_en.append("ALTO EN AZÚCARES")
                if "GRASAS SATURADAS" in sellos_text:
                    sellos_alto_en.append("ALTO EN GRASAS SATURADAS")
                if "SODIO" in sellos_text:
                    sellos_alto_en.append("ALTO EN SODIO")
                if "CALORÍAS" in sellos_text or "CALORIAS" in sellos_text:
                    sellos_alto_en.append("ALTO EN CALORÍAS")
            except NoSuchElementException:
                # Si no se encuentra la sección, intentar buscar imágenes de sellos
                try:
                    sellos_images = self.driver.find_elements(By.XPATH, "//img[contains(@alt, 'ALTO EN')]")
                    for img in sellos_images:
                        alt_text = img.get_attribute('alt')
                        if alt_text and "ALTO EN" in alt_text:
                            sellos_alto_en.append(alt_text.strip())
                except:
                    pass
            
            # Obtener información nutricional
            info_nutricional = {}
            try:
                # Hacer clic en la pestaña de información nutricional si existe
                try:
                    nutrition_tab = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Información Nutricional')]")
                    nutrition_tab.click()
                    time.sleep(1)
                except:
                    pass
                
                # Buscar la tabla de información nutricional
                nutrition_table = self.driver.find_element(By.XPATH, "//p[contains(text(), 'Información Nutricional')]/following-sibling::table")
                
                # Extraer filas de la tabla
                rows = nutrition_table.find_elements(By.TAG_NAME, "tr")
                
                for row in rows[1:]:  # Saltar la fila de encabezado
                    try:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) >= 2:
                            nutrient = cells[0].text.strip()
                            value_100g = cells[1].text.strip() if len(cells) >= 2 else ""
                            
                            # Limpiar y normalizar el nombre del nutriente
                            nutrient = re.sub(r'\s+', ' ', nutrient).strip()
                            
                            # Extraer solo el valor numérico
                            value_match = re.search(r'(\d+(?:\.\d+)?)', value_100g)
                            if value_match:
                                value = float(value_match.group(1))
                                info_nutricional[nutrient] = value
                    except:
                        continue
            except NoSuchElementException:
                pass
            
            # Obtener declaración de alérgenos
            alergenos = "No disponible"
            try:
                alergenos_section = self.driver.find_element(By.XPATH, "//p[contains(text(), 'Declaración de Alérgenos')]/following-sibling::p")
                alergenos = alergenos_section.text.strip()
            except NoSuchElementException:
                pass
            
            # Obtener ingredientes
            ingredientes = "No disponible"
            try:
                ingredientes_section = self.driver.find_element(By.XPATH, "//p[contains(text(), 'Ingredientes')]/following-sibling::p")
                ingredientes = ingredientes_section.text.strip()
            except NoSuchElementException:
                pass
            
            # Crear objeto con los detalles del producto
            product_details = {
                'name': product_name,
                'brand': product_brand,
                'price': product_price,
                'url': product_url,
                'sellos_alto_en': sellos_alto_en,
                'num_sellos': len(sellos_alto_en),
                'info_nutricional': info_nutricional,
                'alergenos': alergenos,
                'ingredientes': ingredientes
            }
            
            return product_details
            
        except Exception as e:
            print(f"Error al obtener detalles del producto: {str(e)}")
            return None
    
    def filter_products_by_sellos(self, products, max_sellos=2):
        """
        Filtra los productos por número de sellos "ALTO EN"
        
        Args:
            products (list): Lista de productos con detalles
            max_sellos (int): Número máximo de sellos permitidos
        
        Returns:
            list: Lista de productos filtrados
        """
        filtered_products = []
        
        for product in products:
            if product and 'num_sellos' in product and product['num_sellos'] <= max_sellos:
                filtered_products.append(product)
        
        return filtered_products
    
    def save_to_csv(self, products, filename="productos_lider_max_2_sellos.csv"):
        """
        Guarda los productos en un archivo CSV
        
        Args:
            products (list): Lista de productos
            filename (str): Nombre del archivo CSV
        
        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        try:
            # Convertir a DataFrame
            df = pd.DataFrame(products)
            
            # Convertir columnas de listas y diccionarios a formato string
            for col in df.columns:
                if df[col].apply(lambda x: isinstance(x, (list, dict))).any():
                    df[col] = df[col].apply(lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, (list, dict)) else x)
            
            # Guardar a CSV
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            
            print(f"Datos guardados correctamente en {filename}")
            return True
            
        except Exception as e:
            print(f"Error al guardar datos en CSV: {str(e)}")
            return False
    
    def close(self):
        """Cierra el navegador"""
        if self.driver:
            self.driver.quit()


def main():
    """Función principal"""
    # Inicializar el scraper
    scraper = LiderScraper(headless=True)
    
    try:
        # Obtener categorías
        categories = scraper.get_categories()
        
        if not categories:
            print("No se pudieron obtener las categorías. Utilizando categorías predefinidas.")
            # Categorías predefinidas en caso de que falle la obtención automática
            categories = [
                {'name': 'Despensa', 'url': 'https://www.lider.cl/supermercado/category/Despensa'},
                {'name': 'Lácteos y Huevos', 'url': 'https://www.lider.cl/supermercado/category/Lácteos-y-Huevos'},
                {'name': 'Frutas y Verduras', 'url': 'https://www.lider.cl/supermercado/category/Frutas-y-Verduras'},
                {'name': 'Carnes', 'url': 'https://www.lider.cl/supermercado/category/Carnes'},
                {'name': 'Congelados', 'url': 'https://www.lider.cl/supermercado/category/Congelados'}
            ]
        
        # Limitar a algunas categorías para pruebas
        test_categories = categories[:3]
        
        all_products = []
        detailed_products = []
        
        # Obtener productos de cada categoría
        for category in test_categories:
            print(f"Obteniendo productos de la categoría: {category['name']}")
            category_products = scraper.get_products_from_category(category['url'], max_pages=2)
            all_products.extend(category_products)
            
            # Limitar a algunos productos por categoría para pruebas
            test_products = category_products[:5]
            
            # Obtener detalles de cada producto
            for product in test_products:
                print(f"Obteniendo detalles del producto: {product['name']}")
                product_details = scraper.get_product_details(product['url'])
                if product_details:
                    detailed_products.append(product_details)
        
        # Filtrar productos con máximo 2 sellos "ALTO EN"
        filtered_products = scraper.filter_products_by_sellos(detailed_products, max_sellos=2)
        
        # Guardar productos filtrados en CSV
        scraper.save_to_csv(filtered_products, "productos_lider_max_2_sellos.csv")
        
        print(f"Se encontraron {len(filtered_products)} productos con máximo 2 sellos 'ALTO EN'")
        
    except Exception as e:
        print(f"Error en la ejecución principal: {str(e)}")
    
    finally:
        # Cerrar el navegador
        scraper.close()


if __name__ == "__main__":
    main()
