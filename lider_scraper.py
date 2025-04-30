#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Lider Product Scraper

Este script extrae datos de productos del sitio web de Lider.cl, filtrando aquellos
que tienen máximo 2 sellos "ALTO EN" según la Ley 20.606.

Fecha: Abril 2025
"""

import time
import re
import json
import random
import pandas as pd
from selenium import webdriver
# from selenium.webdriver.chrome.service import Service # No longer needed for basic Selenium Manager usage
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains # Importar ActionChains
# from webdriver_manager.chrome import ChromeDriverManager # No longer needed

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
        self.login_url = "https://www.lider.cl/supermercado/login" # Added login URL
        self.categories = []
        self.products = []
        
        # Configurar opciones de Chrome
        chrome_options = Options()
        if headless:
            print("Ejecutando en modo headless.")
            chrome_options.add_argument("--headless=new") # Use new headless mode
        else:
            print("Ejecutando en modo NO headless (con interfaz gráfica visible).")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        
        # Configuraciones para evitar detección de bot
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36') # Match browser version

        # Inicializar el driver usando Selenium Manager (automatic driver handling)
        try:
            print("Inicializando ChromeDriver usando Selenium Manager (gestión automática)...")
            self.driver = webdriver.Chrome(options=chrome_options)
            print("ChromeDriver inicializado correctamente.")
        except Exception as e:
            print(f"Error al inicializar ChromeDriver con Selenium Manager: {e}")
            raise # Re-raise the exception if initialization fails
            
        self.driver.implicitly_wait(implicit_wait)
        
        # Modificar el navigator.webdriver para evitar detección
        try:
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception as script_err:
            print(f"Advertencia: No se pudo ejecutar el script para ocultar navigator.webdriver: {script_err}")

    def login(self, email, password):
        """
        Inicia sesión en Lider.cl usando la página de login directa.
        
        Args:
            email (str): Correo electrónico
            password (str): Contraseña
        
        Returns:
            bool: True si el inicio de sesión fue exitoso, False en caso contrario
        """
        try:
            print(f"Navegando a la página de login: {self.login_url}")
            self.driver.get(self.login_url)
            time.sleep(random.uniform(3, 5)) # Pausa aleatoria más larga para login
            
            # Manejar posible captcha ANTES de interactuar con el formulario
            if not self._handle_captcha():
                print("No se pudo resolver el captcha en la página de login.")
                return False
            
            # Esperar a que aparezca el formulario de inicio de sesión
            print("Buscando campos de email y contraseña...")
            email_input = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            print("Campo email encontrado.")
            email_input.send_keys(email)
            time.sleep(random.uniform(0.5, 1.5))
            
            password_input = self.driver.find_element(By.ID, "password")
            print("Campo contraseña encontrado.")
            password_input.send_keys(password)
            time.sleep(random.uniform(0.5, 1.5))
            
            # Hacer clic en el botón de inicio de sesión del formulario
            print("Buscando botón de submit...")
            submit_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
            )
            print("Botón de submit encontrado, haciendo clic...")
            # Usar JS click por si acaso
            self.driver.execute_script("arguments[0].click();", submit_button)
            # submit_button.click()
            
            # Esperar a que se complete el inicio de sesión (buscar un elemento que indique sesión iniciada)
            # Puede ser el botón "Mi Cuenta" o la redirección a la página principal/dashboard
            print("Esperando confirmación de inicio de sesión...")
            WebDriverWait(self.driver, 25).until(
                EC.any_of(
                    EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Mi Cuenta')] | //a[contains(@href, '/cuenta/dashboard')] | //*[contains(text(), 'Hola,')] ")),
                    EC.url_contains("/supermercado") # Check if redirected back to supermarket
                )
            )
            
            # Verificar si aún estamos en la página de login (indicativo de fallo)
            if "/login" in self.driver.current_url:
                print("Error: Aún en la página de login después del intento. Credenciales incorrectas?")
                self.driver.save_screenshot("error_login_failed.png")
                return False
                
            print("Inicio de sesión exitoso (o al menos no estamos en la página de login).")
            # Manejar captcha que puede aparecer DESPUÉS del login
            time.sleep(random.uniform(2, 4))
            self._handle_captcha() # Intentar manejar captcha post-login, no crítico si falla aquí
            return True
            
        except TimeoutException as e:
            print(f"Timeout durante el inicio de sesión: {str(e)}")
            self.driver.save_screenshot("error_login_timeout.png")
            return False
        except Exception as e:
            import traceback
            print(f"Error inesperado al iniciar sesión: {str(e)}")
            print(traceback.format_exc())
            self.driver.save_screenshot("error_login_unexpected.png")
            return False
    
    def _handle_captcha(self):
        """
        Maneja el captcha de PerimeterX si aparece, intentando resolverlo automáticamente.
        Busca tanto el div contenedor como el iframe modal.
        Usa selector más específico para el botón.
        
        Returns:
            bool: True si se manejó correctamente o no hubo captcha, False si falló.
        """
        captcha_found = False
        captcha_iframe = None
        try:
            # Esperar un poco para que el captcha aparezca si es que lo hace
            time.sleep(random.uniform(3, 5))
            
            # Verificar si hay un captcha presente (buscando el iframe modal O el div contenedor)
            try:
                print("Buscando iframe modal de captcha (#px-captcha-modal)...")
                captcha_iframe = WebDriverWait(self.driver, 7).until(
                    EC.presence_of_element_located((By.ID, "px-captcha-modal"))
                )
                print("Captcha (iframe modal) detectado.")
                captcha_found = True
            except TimeoutException:
                print("No se encontró iframe modal. Buscando div contenedor de captcha (div.px-captcha-container)...")
                try:
                    captcha_container = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.px-captcha-container"))
                    )
                    print("Captcha (div contenedor) detectado.")
                    try:
                        captcha_iframe = WebDriverWait(captcha_container, 5).until(
                            EC.presence_of_element_located((By.XPATH, ".//iframe[contains(@title, 'verificación humana') or contains(@title, 'Human Challenge')]"))
                        )
                        print("Iframe encontrado dentro del div contenedor.")
                        captcha_found = True
                    except TimeoutException:
                        print("No se encontró iframe dentro del div contenedor. El captcha puede ser diferente.")
                        return False # Fallo si no hay iframe en el contenedor
                except TimeoutException:
                    print("No se detectó ningún tipo de captcha conocido.")
                    return True # No hay captcha

            # Si encontramos un captcha (iframe modal o iframe dentro de div)
            if captcha_found and captcha_iframe:
                print("Intentando resolver captcha...")
                try:
                    # Cambiar al iframe
                    self.driver.switch_to.frame(captcha_iframe)
                    print("Cambiado al iframe del captcha.")
                    time.sleep(random.uniform(2, 4)) # Aumentar pausa dentro del iframe

                    # Localizar el botón "Mantén presionado" (selector más específico)
                    print("Buscando botón 'Mantén presionado unos segundos' dentro del iframe...")
                    hold_button = WebDriverWait(self.driver, 15).until( # Espera 15 seg
                        EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Mantén presionado unos segundos']"))
                    )
                    print("Botón de captcha encontrado.")
                    
                    # Simular mantener presionado el botón
                    actions = ActionChains(self.driver)
                    hold_time = random.uniform(7.5, 10.5) # Ajustar ligeramente el tiempo
                    print(f"Manteniendo presionado por {hold_time:.2f} segundos...")
                    actions.click_and_hold(hold_button).pause(hold_time).release().perform()
                    print("Botón soltado.")
                    
                    # Volver al contenido principal
                    self.driver.switch_to.default_content()
                    print("Regresado al contenido principal.")
                    time.sleep(random.uniform(4, 7)) # Aumentar espera después de resolver

                    # Verificar si el captcha desapareció (verificar ambos tipos)
                    try:
                        WebDriverWait(self.driver, 12).until_not( # Aumentar espera para desaparición
                            EC.any_of(
                                EC.presence_of_element_located((By.ID, "px-captcha-modal")),
                                EC.presence_of_element_located((By.CSS_SELECTOR, "div.px-captcha-container"))
                            )
                        )
                        print("Captcha resuelto exitosamente.")
                        return True
                    except TimeoutException:
                        print("El captcha no desapareció después del intento.")
                        self.driver.save_screenshot("error_captcha_persist.png")
                        return False

                except TimeoutException as e:
                    print(f"No se encontró el botón del captcha ('Mantén presionado unos segundos') dentro del iframe después de 15 segundos: {e}")
                    try:
                        self.driver.save_screenshot("error_captcha_iframe_content.png")
                        print("Screenshot del contenido del iframe guardado en 'error_captcha_iframe_content.png'")
                    except Exception as ss_err:
                        print(f"No se pudo guardar el screenshot del iframe: {ss_err}")
                    finally:
                        try: self.driver.switch_to.default_content()
                        except: pass
                    return False
                except Exception as e:
                    print(f"Error inesperado al interactuar con el captcha: {e}")
                    try: self.driver.switch_to.default_content()
                    except: pass
                    self.driver.save_screenshot("error_captcha_interaction.png")
                    return False
            else:
                print("No se encontró captcha o iframe asociado.")
                return True # Asumir que no hay captcha si no se encontró nada
            
        except Exception as e:
            print(f"Error general al manejar el captcha: {str(e)}")
            self.driver.save_screenshot("error_captcha_general.png")
            try: self.driver.switch_to.default_content()
            except: pass
            return False
    
    def get_categories(self):
        """
        Obtiene las categorías de productos
        
        Returns:
            list: Lista de categorías
        """
        try:
            # Asegurarse de estar en la página principal del supermercado
            if "/supermercado" not in self.driver.current_url:
                print(f"Navegando a la página principal: {self.base_url}")
                self.driver.get(self.base_url)
                time.sleep(random.uniform(2, 4))
            else:
                print("Ya estamos en la página del supermercado.")
                time.sleep(random.uniform(1, 2))
            
            # Manejar posible captcha ANTES de cualquier interacción
            if not self._handle_captcha():
                print("No se pudo resolver el captcha al obtener categorías. Terminando.")
                return []
            
            # Hacer clic en el botón de categorías
            print("Buscando botón de categorías...")
            try:
                categories_button = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Categorías')]"))
                )
                print("Botón de categorías encontrado, haciendo clic...")
                self.driver.execute_script("arguments[0].click();", categories_button)
                time.sleep(random.uniform(1.5, 3.5))
            except ElementClickInterceptedException as e:
                 print(f"Error de intercepción al hacer clic en Categorías: {e}")
                 print("Intentando resolver captcha nuevamente...")
                 if not self._handle_captcha():
                     print("Fallo al resolver captcha después de intercepción.")
                     self.driver.save_screenshot("error_categories_intercept_fail.png")
                     return []
                 try:
                     categories_button = WebDriverWait(self.driver, 10).until(
                         EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Categorías')]"))
                     )
                     self.driver.execute_script("arguments[0].click();", categories_button)
                     time.sleep(random.uniform(1.5, 3.5))
                 except Exception as e2:
                     print(f"Fallo al hacer clic en Categorías incluso después de reintentar: {e2}")
                     self.driver.save_screenshot("error_categories_retry_fail.png")
                     return []
            except Exception as e:
                 print(f"Error inesperado al buscar/hacer clic en Categorías: {e}")
                 self.driver.save_screenshot("error_categories_click.png")
                 return []

            # Esperar a que se carguen las categorías
            print("Esperando que se carguen las categorías...")
            category_elements = WebDriverWait(self.driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='/supermercado/category/']")) # Selector más específico para Lider
            )
            print(f"Encontrados {len(category_elements)} elementos de categoría.")
            
            # Extraer información de las categorías
            self.categories = []
            for i, element in enumerate(category_elements):
                try:
                    name = element.text.strip()
                    url = element.get_attribute('href')
                    if name and url and '/supermercado/category/' in url:
                        category = {
                            'name': name,
                            'url': url
                        }
                        if url not in [c['url'] for c in self.categories]:
                           self.categories.append(category)
                except StaleElementReferenceException:
                    print(f"Elemento de categoría {i+1} obsoleto, reintentando búsqueda...")
                    category_elements = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='/supermercado/category/']"))
                    )
                    continue 
                except Exception as e:
                    print(f"Error procesando categoría {i+1}: {e}")
            
            print(f"Se encontraron {len(self.categories)} categorías únicas.")
            # Cerrar el menú de categorías si sigue abierto (opcional)
            try:
                print("Intentando cerrar menú de categorías...")
                body_element = self.driver.find_element(By.TAG_NAME, 'body')
                ActionChains(self.driver).move_to_element_with_offset(body_element, 5, 5).click().perform()
                time.sleep(random.uniform(0.5, 1))
                print("Menú de categorías cerrado (o no estaba abierto).")
            except Exception as close_err:
                 print(f"No se pudo cerrar el menú de categorías (puede que no fuera necesario): {close_err}")
                
            return self.categories
            
        except Exception as e:
            import traceback
            print(f"Error al obtener categorías: {str(e)}")
            print(traceback.format_exc())
            self.driver.save_screenshot("error_categories.png")
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
        category_products = []
        try:
            print(f"Navegando a la categoría: {category_url}")
            self.driver.get(category_url)
            time.sleep(random.uniform(2, 4))
            
            # Manejar posible captcha
            if not self._handle_captcha():
                print(f"No se pudo resolver el captcha en la categoría: {category_url}")
                return []
            
            current_page = 1
            
            while current_page <= max_pages:
                print(f"Scrapeando página {current_page} de la categoría: {category_url}")
                # Esperar a que se carguen los productos
                try:
                    WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='product-card']")) # Selector más genérico
                    )
                    time.sleep(random.uniform(3, 5)) # Dar tiempo extra para carga completa (JS, imágenes)
                except TimeoutException:
                    print(f"Timeout esperando productos en la página {current_page} de {category_url}")
                    if current_page == 1:
                        print("No se encontraron productos en la primera página.")
                    break # Salir si no cargan productos
                
                # Obtener los elementos de productos
                product_elements = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='product-card']")
                print(f"Encontrados {len(product_elements)} elementos de producto en la página.")
                
                if not product_elements:
                    print("No se encontraron productos en esta página (después de la espera inicial), terminando categoría.")
                    break

                # Extraer información de los productos
                for element in product_elements:
                    try:
                        # Obtener URL del producto
                        product_link = "URL no disponible"
                        try:
                            product_link_element = element.find_element(By.CSS_SELECTOR, "a")
                            product_link = product_link_element.get_attribute('href')
                        except NoSuchElementException: pass
                        
                        # Obtener nombre del producto
                        product_name = "Nombre no disponible"
                        try:
                            product_name = element.find_element(By.CSS_SELECTOR, "span[class*='product-name'], div[class*='product-name'], h3[class*='product-title']").text.strip()
                        except NoSuchElementException: pass
                        
                        # Obtener precio del producto
                        product_price = "Precio no disponible"
                        try:
                            price_selectors = ["span[class*='price']", "div[class*='price']", "p[class*='price']"]
                            for selector in price_selectors:
                                try:
                                    price_text = element.find_element(By.CSS_SELECTOR, selector).text.strip()
                                    product_price = price_text.split('\n')[0]
                                    if product_price: break
                                except NoSuchElementException:
                                    continue
                        except NoSuchElementException: pass
                        
                        # Obtener marca del producto
                        product_brand = "Marca no disponible"
                        try:
                            product_brand = element.find_element(By.CSS_SELECTOR, "div[class*='product-brand'], span[class*='brand']").text.strip()
                        except NoSuchElementException: pass
                        
                        # Crear objeto de producto
                        if product_link != "URL no disponible" and product_name != "Nombre no disponible":
                            product = {
                                'name': product_name,
                                'brand': product_brand,
                                'price': product_price,
                                'url': product_link,
                                'category': category_url.split('/category/')[-1] # Extraer nombre de categoría de URL
                            }
                            category_products.append(product)
                        
                    except StaleElementReferenceException:
                        print("Elemento de producto obsoleto, saltando...")
                        continue
                    except Exception as e:
                        print(f"Error al procesar un producto: {str(e)}")
                
                # Verificar si hay más páginas y navegar a la siguiente
                if current_page >= max_pages:
                    print(f"Alcanzado el límite de {max_pages} páginas.")
                    break
                    
                try:
                    # Buscar botón "Siguiente" o paginación
                    next_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Next page') or contains(., 'Siguiente') or contains(@class, 'next')]"))
                    )
                    if next_button.is_enabled():
                        print("Navegando a la siguiente página...")
                        try:
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                            time.sleep(random.uniform(0.5, 1))
                            self.driver.execute_script("arguments[0].click();", next_button)
                        except Exception as click_err:
                            print(f"Error al hacer clic en 'Siguiente' (JS click): {click_err}. Terminando categoría.")
                            break
                                
                        current_page += 1
                        time.sleep(random.uniform(3, 6))  # Esperar a que se cargue la siguiente página
                    else:
                        print("Botón 'Siguiente' deshabilitado.")
                        break
                except TimeoutException:
                    print("No se encontró el botón 'Siguiente'. Terminando categoría.")
                    break # No hay botón siguiente o no es clickeable a tiempo
                except Exception as e:
                    print(f"Error al intentar ir a la siguiente página: {e}")
                    break
            
            print(f"Se encontraron {len(category_products)} productos en total en la categoría {category_url}")
            return category_products
            
        except Exception as e:
            import traceback
            print(f"Error general al obtener productos de la categoría {category_url}: {str(e)}")
            print(traceback.format_exc())
            self.driver.save_screenshot(f"error_category_{category_url.split('/category/')[-1]}.png")
            return category_products # Devolver lo que se haya podido recolectar
    
    def get_product_details(self, product_url):
        """
        Obtiene los detalles de un producto (incluyendo sellos e info nutricional)
        
        Args:
            product_url (str): URL del producto
        
        Returns:
            dict: Detalles del producto, incluyendo 'sellos_count' y 'info_nutricional'
        """
        details = {
            'url': product_url,
            'name': 'No disponible',
            'brand': 'No disponible',
            'price': 'No disponible',
            'sellos_alto_en': [],
            'sellos_count': 0,
            'info_nutricional': {}
        }
        try:
            print(f"  Navegando a la página del producto: {product_url}")
            self.driver.get(product_url)
            time.sleep(random.uniform(2, 4))
            
            # Manejar posible captcha
            if not self._handle_captcha():
                print(f"  No se pudo resolver el captcha en la página del producto: {product_url}")
                # Continuar de todos modos, puede que la info principal esté disponible
            
            # Esperar a que se cargue la página del producto (buscar un contenedor principal)
            print("  Esperando carga de detalles del producto...")
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='product-detail'], main[id='main-content'], div[class*='product-sheet']"))
            )
            time.sleep(random.uniform(2, 4)) # Tiempo extra para carga completa
            
            # Obtener información básica del producto
            try:
                details['name'] = self.driver.find_element(By.CSS_SELECTOR, "h1[class*='product-name'], h1[class*='title']").text.strip()
            except NoSuchElementException: pass
            
            try:
                details['brand'] = self.driver.find_element(By.CSS_SELECTOR, "a[href*='/brand/'], span[class*='brand']").text.strip()
            except NoSuchElementException: pass
            
            try:
                price_selectors = ["span[class*='price']", "div[class*='price']", "p[class*='price']"]
                for selector in price_selectors:
                     try:
                         price_text = self.driver.find_element(By.CSS_SELECTOR, selector).text.strip()
                         details['price'] = price_text.split('\n')[0] # Tomar primer precio
                         if details['price']: break
                     except NoSuchElementException:
                         continue
            except NoSuchElementException: pass
            
            # Obtener sellos "ALTO EN"
            sellos_alto_en = []
            try:
                try:
                    sellos_images = self.driver.find_elements(By.XPATH, "//img[contains(@alt, 'ALTO EN') or contains(@src, 'sello') or contains(@class, 'stamp')]")
                    if sellos_images:
                        for img in sellos_images:
                            alt_text = img.get_attribute('alt')
                            if alt_text and "ALTO EN" in alt_text.upper():
                                sello = alt_text.strip().upper()
                                if sello not in sellos_alto_en:
                                    sellos_alto_en.append(sello)
                    else:
                         sellos_section = self.driver.find_element(By.XPATH, "//p[contains(., 'Sellos \"ALTO EN\"') or contains(., 'Sellos de advertencia')]/following-sibling::p | //div[contains(@class, 'stamps')] | //div[contains(text(), 'Sellos')] ")
                         sellos_text = sellos_section.text.strip().upper()
                         if "AZÚCARES" in sellos_text or "AZUCARES" in sellos_text:
                             sellos_alto_en.append("ALTO EN AZÚCARES")
                         if "GRASAS SATURADAS" in sellos_text:
                             sellos_alto_en.append("ALTO EN GRASAS SATURADAS")
                         if "SODIO" in sellos_text:
                             sellos_alto_en.append("ALTO EN SODIO")
                         if "CALORÍAS" in sellos_text or "CALORIAS" in sellos_text:
                             sellos_alto_en.append("ALTO EN CALORÍAS")
                except NoSuchElementException:
                    print("    No se encontró sección/imágenes de sellos.")
                except Exception as img_err:
                    print(f"    Error buscando sellos: {img_err}")

            except Exception as sello_err:
                 print(f"    Error general buscando sellos: {sello_err}")
            
            details['sellos_alto_en'] = list(set(sellos_alto_en)) # Eliminar duplicados
            details['sellos_count'] = len(details['sellos_alto_en'])
            print(f"    Sellos contados: {details['sellos_count']} {details['sellos_alto_en']}")

            # Obtener información nutricional
            info_nutricional = {}
            try:
                print("  Buscando información nutricional...")
                try:
                    nutrition_trigger = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Información Nutricional')] | //div[contains(., 'Información Nutricional')] | //*[contains(@id, 'nutritional')] | //*[contains(text(), 'Nutrición')]"))
                    )
                    print("    Encontrado disparador de info nutricional, haciendo clic...")
                    try:
                         WebDriverWait(self.driver, 1).until(
                             EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'nutritional-info-content')]//table | //table[contains(@class, 'nutrition-table')]"))
                         )
                         print("    Info nutricional ya visible.")
                    except TimeoutException:
                         self.driver.execute_script("arguments[0].click();", nutrition_trigger) # Usar JS click
                         time.sleep(random.uniform(1, 2))
                except TimeoutException:
                    print("    No se encontró pestaña/botón de Información Nutricional clickeable.")
                except Exception as click_err:
                    print(f"    Error al hacer clic en pestaña nutricional: {click_err}")
                
                nutrition_container = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'nutritional-info-content')]//table | //table[contains(@class, 'nutrition-table')] | //div[contains(@id, 'nutritional-info')] | //section[contains(., 'Información Nutricional')]"))
                )
                
                try:
                    rows = nutrition_container.find_elements(By.TAG_NAME, "tr")
                    if len(rows) > 1:
                        headers = [th.text.strip() for th in rows[0].find_elements(By.TAG_NAME, "th")]
                        value_col_index = 1 
                        if len(headers) > 1 and ('100 g' in headers[1] or '100 ml' in headers[1]):
                            value_col_index = 1
                        elif len(headers) > 2 and ('100 g' in headers[2] or '100 ml' in headers[2]):
                             value_col_index = 2
                        
                        for row in rows[1:]:
                            try:
                                cells = row.find_elements(By.XPATH, ".//td | .//th")
                                if len(cells) > value_col_index:
                                    nutrient = cells[0].text.strip()
                                    value_text = cells[value_col_index].text.strip()
                                    nutrient = re.sub(r'\s*:\s*$', '', nutrient).strip()
                                    nutrient = re.sub(r'\s+', ' ', nutrient).strip()
                                    value_match = re.search(r'(\d+(?:[.,]\d+)?)', value_text)
                                    if value_match and nutrient:
                                        value_str = value_match.group(1).replace(',', '.')
                                        try:
                                            value = float(value_str)
                                            info_nutricional[nutrient] = value
                                        except ValueError:
                                            print(f"      No se pudo convertir '{value_str}' a float para {nutrient}")
                            except Exception as row_err:
                                print(f"    Error procesando fila de tabla nutricional: {row_err}")
                                continue
                    else:
                         items = nutrition_container.find_elements(By.XPATH, ".//div | .//p | .//span")
                         current_nutrient = None
                         for item in items:
                             text = item.text.strip()
                             if not text: continue
                             match = re.match(r'([^:]+):\s*(\d+(?:[.,]\d+)?.*)', text, re.IGNORECASE)
                             if match:
                                 nutrient = match.group(1).strip()
                                 value_text = match.group(2).strip()
                                 value_match = re.search(r'(\d+(?:[.,]\d+)?)', value_text)
                                 if value_match and nutrient:
                                     value_str = value_match.group(1).replace(',', '.')
                                     try:
                                         value = float(value_str)
                                         info_nutricional[nutrient] = value
                                         current_nutrient = None
                                     except ValueError:
                                         print(f"      No se pudo convertir '{value_str}' a float para {nutrient}")
                                 continue
                             if re.search(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', text) and len(text) > 3 and not re.search(r'\d', text):
                                 current_nutrient = text
                             elif current_nutrient and re.search(r'^\d+(?:[.,]\d+)?', text):
                                 value_match = re.search(r'(\d+(?:[.,]\d+)?)', text)
                                 if value_match:
                                     value_str = value_match.group(1).replace(',', '.')
                                     try:
                                         value = float(value_str)
                                         info_nutricional[current_nutrient] = value
                                         current_nutrient = None
                                     except ValueError:
                                         print(f"      No se pudo convertir '{value_str}' a float para {current_nutrient}")
                                         current_nutrient = None
                except Exception as table_err:
                    print(f"    Error extrayendo datos de la tabla/contenedor nutricional: {table_err}")

            except NoSuchElementException:
                print("    No se encontró sección de información nutricional.")
            except Exception as e:
                import traceback
                print(f"    Error al obtener información nutricional: {str(e)}")
                print(traceback.format_exc())
            
            details['info_nutricional'] = info_nutricional
            return details
            
        except Exception as e:
            import traceback
            print(f"Error general al obtener detalles del producto {product_url}: {str(e)}")
            print(traceback.format_exc())
            self.driver.save_screenshot(f"error_product_{product_url.split('/')[-1]}.png")
            return details # Devolver detalles parciales

    def filter_products(self, products, max_sellos=2):
        """
        Filtra los productos para mantener solo aquellos con máximo N sellos "ALTO EN"
        Utiliza la información de 'sellos_count' si está disponible.
        
        Args:
            products (list): Lista de diccionarios de productos con detalles
            max_sellos (int): Número máximo de sellos permitidos (default: 2)
        
        Returns:
            list: Lista filtrada de productos
        """
        valid_products = []
        for p in products:
            try:
                sello_count = int(p.get('sellos_count', 99))
                if sello_count <= max_sellos:
                    valid_products.append(p)
            except (ValueError, TypeError):
                print(f"Advertencia: 'sellos_count' inválido ({p.get('sellos_count')}) para producto {p.get('name')}. Excluyendo.")
                continue
                
        print(f"Filtrados {len(products) - len(valid_products)} productos por tener más de {max_sellos} sellos o conteo inválido. Quedan {len(valid_products)}.")
        return valid_products

    def save_to_excel(self, products, filename="lider_productos_filtrados.xlsx"):
        """
        Guarda la lista de productos en un archivo Excel
        
        Args:
            products (list): Lista de diccionarios de productos
            filename (str): Nombre del archivo Excel de salida
        """
        if not products:
            print("No hay productos para guardar.")
            return
            
        try:
            df = pd.DataFrame(products)
            
            if 'info_nutricional' in df.columns and df['info_nutricional'].apply(lambda x: isinstance(x, dict) and x).any():
                try:
                    df_nutri = pd.json_normalize(df['info_nutricional']).add_prefix('Nutri_')
                    df = pd.concat([df.drop('info_nutricional', axis=1), df_nutri], axis=1)
                except Exception as norm_err:
                    print(f"Error al normalizar info_nutricional: {norm_err}. Se guardará como JSON.")
                    df['info_nutricional'] = df['info_nutricional'].apply(lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, dict) else x)
            elif 'info_nutricional' in df.columns:
                 df = df.drop('info_nutricional', axis=1)

            cols_order = [
                'name', 'brand', 'price', 'category', 'url', 
                'sellos_count', 'sellos_alto_en'
            ]
            nutri_cols = sorted([col for col in df.columns if col.startswith('Nutri_')])
            final_cols_order = cols_order + nutri_cols
            
            existing_cols = [c for c in final_cols_order if c in df.columns]
            remaining_cols = sorted([c for c in df.columns if c not in existing_cols])
            df = df[existing_cols + remaining_cols]

            for col in df.select_dtypes(include=['object']).columns:
                 if df[col].apply(lambda x: isinstance(x, (list, dict))).any():
                     df[col] = df[col].apply(lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, (list, dict)) else x)
            
            print(f"Guardando datos en {filename}...")
            df.to_excel(filename, index=False, engine='openpyxl')
            print(f"Datos guardados exitosamente en {filename}")
        except Exception as e:
            import traceback
            print(f"Error al guardar en Excel: {str(e)}")
            print(traceback.format_exc())

    def close(self):
        """
        Cierra el navegador
        """
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
                print("Navegador cerrado.")
            except Exception as e:
                print(f"Error al cerrar el navegador: {e}")
        else:
            print("El navegador no estaba inicializado o ya estaba cerrado.")

# Ejemplo de uso (se ejecutará desde run_lider_scraper.py)
if __name__ == '__main__':
    
    # --- Configuración --- (Estos valores son sobrescritos por run_lider_scraper.py)
    EMAIL = "tu_email@ejemplo.com" 
    PASSWORD = "tu_contraseña"    
    USE_LOGIN = False             
    HEADLESS_MODE = False         
    MAX_PAGES_PER_CATEGORY = 1    
    OUTPUT_FILE = "lider_productos_test.xlsx"
    MAX_CATEGORIES_TO_SCRAPE = 2  
    MAX_SELLOS_ALLOWED = 2
    # ---------------------

    scraper = None # Inicializar a None
    try:
        scraper = LiderScraper(headless=HEADLESS_MODE)
        all_products_details = []

        if USE_LOGIN:
            if not scraper.login(EMAIL, PASSWORD):
                print("Fallo en el inicio de sesión, terminando script.")
                exit()
            time.sleep(2)
        
        categories = scraper.get_categories()
        
        if not categories:
            print("No se pudieron obtener categorías, terminando script.")
        else:
            categories_to_scrape = categories[:MAX_CATEGORIES_TO_SCRAPE] 
            print(f"\nScrapeando las primeras {len(categories_to_scrape)} categorías...")

            for category in categories_to_scrape:
                print(f"\n--- Procesando categoría: {category['name']} ({category['url']}) ---")
                products_in_category = scraper.get_products_from_category(category['url'], max_pages=MAX_PAGES_PER_CATEGORY)
                
                print(f"Obteniendo detalles para {len(products_in_category)} productos...")
                for i, product in enumerate(products_in_category):
                    print(f"  Detalle producto {i+1}/{len(products_in_category)}: {product.get('name', 'N/A')}")
                    details = scraper.get_product_details(product['url'])
                    full_details = {**product, **details}
                    all_products_details.append(full_details)
                    time.sleep(random.uniform(1, 3)) # Pausa entre productos

            print(f"\n--- Filtrando productos (máximo {MAX_SELLOS_ALLOWED} sellos) ---")
            filtered_products = scraper.filter_products(all_products_details, max_sellos=MAX_SELLOS_ALLOWED)
            
            print("\n--- Guardando resultados en Excel ---")
            scraper.save_to_excel(filtered_products, filename=OUTPUT_FILE)

    except Exception as e:
        import traceback
        print(f"\nError principal en el script: {str(e)}")
        print(traceback.format_exc())
    finally:
        if scraper:
             scraper.close()
        else:
             print("Scraper no inicializado, no se requiere cierre.")

