import csv
import time
import datetime
import os
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

def check_for_captcha(driver):
    try:
        # Detectar diferentes tipos de CAPTCHAs en Lider
        captcha_texts = [
            "¿Persona o robot?", 
            "necesitamos confirmar que eres humano",
            "Mantén presionado unos segundos"
        ]
        
        for text in captcha_texts:
            captcha_elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
            if captcha_elements:
                print(f"¡CAPTCHA detectado! Texto encontrado: '{text}'")
                print("Por favor resuelve el captcha manualmente.")
                print("Una vez resuelto, presiona Enter para continuar...")
                input("→ Presiona Enter cuando hayas resuelto el captcha...")
                time.sleep(3)  # Dar tiempo para que la página se actualice después de resolver el CAPTCHA
                return True
                
        # Verificar si hay botones o elementos relacionados con CAPTCHAs
        captcha_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Mantén presionado')]")
        if captcha_buttons:
            print("¡Botón de CAPTCHA detectado! Por favor mantén presionado el botón hasta completar la verificación.")
            input("→ Presiona Enter cuando hayas resuelto el captcha...")
            time.sleep(3)
            return True
            
    except Exception as e:
        print(f"Error al verificar CAPTCHA: {e}")
    return False

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

    driver = None
    scraped = []
    
    try:
        # Crear directorio temporal para Chrome si no existe
        user_data_dir = os.path.join(os.getcwd(), "chrome_data")
        os.makedirs(user_data_dir, exist_ok=True)
        
        # Modificar las opciones del navegador para ser menos detectable
        options = uc.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument(f"--user-data-dir={user_data_dir}")
        # Añadir estas opciones para imitar mejor un navegador real
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Iniciar el driver con una espera más larga
        driver = uc.Chrome(options=options)
        driver.set_page_load_timeout(60)  # Reducir el tiempo de espera, gestionaremos los CAPTCHAs específicamente
        
        base_url = f"https://www.lider.cl/supermercado/search?query={product}&page=1"
        print("Iniciando navegación...")
        driver.get("https://www.lider.cl/")
        
        # Verificar CAPTCHA en la página inicial
        if check_for_captcha(driver):
            print("CAPTCHA inicial resuelto, continuando...")
        
        time.sleep(3)  # Esperar a que cargue el sitio inicial
        
        print(f"Navegando a la URL de búsqueda: {base_url}")
        driver.get(base_url)
        
        # Verificar CAPTCHA después de la búsqueda
        if check_for_captcha(driver):
            print("CAPTCHA de búsqueda resuelto, continuando...")
        
        print("Esperando 10 segundos antes de continuar con el scraping...")
        time.sleep(10)  # Tiempo reducido, ya que ahora manejamos los CAPTCHAs específicamente
        print("Continuando con el scraping...")

        page_number = 1
        while True:
            print(f"Scraping page {page_number}")
            try:
                # Comprobar si hay CAPTCHA antes de procesar la página
                if check_for_captcha(driver):
                    print(f"CAPTCHA resuelto en página {page_number}, continuando...")
                
                # Esperar a que cargue la página
                print("Esperando que los productos carguen...")
                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.product-card')))
                print("Productos cargados, realizando scroll...")
                
                # Hacer scroll para cargar todos los productos
                scroll_down(driver)
                
                # Encontrar los productos
                items = driver.find_elements(By.CSS_SELECTOR, '.product-card')
                print(f"Encontrados {len(items)} productos en la página {page_number}")
                
                if not items:
                    print("No se encontraron productos, verificando otros selectores...")
                    # Intentar con otros selectores comunes si el sitio cambió
                    items = driver.find_elements(By.CSS_SELECTOR, '[data-testid="product-card"]')
                    if not items:
                        print("No se encontraron productos con selectores alternativos. Finaliza el scraping.")
                        break

                for item in items:
                    try:
                        name = item.find_element(By.CSS_SELECTOR, '.product-card__name').text.strip()
                    except Exception:
                        try:
                            name = item.find_element(By.CSS_SELECTOR, '[data-testid="product-name"]').text.strip()
                        except Exception:
                            name = "Name not found"
                    
                    try:
                        brand = item.find_element(By.CSS_SELECTOR, '.product-card__brand').text.strip()
                    except Exception:
                        try:
                            brand = item.find_element(By.CSS_SELECTOR, '[data-testid="product-brand"]').text.strip()
                        except Exception:
                            brand = "Brand not found"
                    
                    try:
                        price = item.find_element(By.CSS_SELECTOR, '.product-card__price--current').text.strip()
                    except Exception:
                        try:
                            price = item.find_element(By.CSS_SELECTOR, '[data-testid="current-price"]').text.strip()
                        except Exception:
                            price = "Price not found"
                    
                    # Limpiar el precio
                    if price != "Price not found":
                        price = price.replace('$', '').replace('.', '').strip()
                    
                    try:
                        reference_price = item.find_element(By.CSS_SELECTOR, '.product-card__price--reference').text.strip()
                    except Exception:
                        try:
                            reference_price = item.find_element(By.CSS_SELECTOR, '[data-testid="reference-price"]').text.strip()
                        except Exception:
                            reference_price = "No Reference Price"
                    
                    # Limpiar el precio de referencia
                    if reference_price != "No Reference Price":
                        reference_price = reference_price.replace('$', '').replace('.', '').strip()
                    
                    if name != "Name not found":
                        scraped.append({
                            'brand': brand,
                            'name': name,
                            'price': price,
                            'reference_price': reference_price,
                            'date': date
                        })
                        print(f'Añadido: {name} - Precio: ${price}')

                # Verificar si hay más páginas
                page_number += 1
                try:
                    print("Buscando botón de página siguiente...")
                    next_buttons = driver.find_elements(By.CSS_SELECTOR, 'button.next')
                    if not next_buttons:
                        next_buttons = driver.find_elements(By.CSS_SELECTOR, '[aria-label="Siguiente página"]')
                    
                    if next_buttons and len(next_buttons) > 0 and next_buttons[0].is_enabled():
                        print("Haciendo clic en el botón de página siguiente")
                        next_buttons[0].click()
                        time.sleep(3)  # Esperar a que cargue la siguiente página
                        
                        # Verificar CAPTCHA después de cambiar de página
                        if check_for_captcha(driver):
                            print(f"CAPTCHA resuelto al cambiar a página {page_number}, continuando...")
                    else:
                        print("No se encontró botón de siguiente página o está deshabilitado. Finalizando el scraping.")
                        break
                except Exception as e:
                    print(f"Error al navegar a la siguiente página: {e}")
                    break

            except Exception as e:
                print(f"Error durante el scraping de la página {page_number}:")
                print(traceback.format_exc())
                break
    
    except Exception as e:
        print(f"Error al inicializar el scraper:")
        print(traceback.format_exc())
    
    finally:
        # Cerrar el navegador de manera segura
        try:
            if driver:
                print("Cerrando el navegador...")
                driver.quit()
                print("Navegador cerrado correctamente")
        except Exception as e:
            print(f"Error al cerrar el navegador: {e}")
    
    return scraped

def run(product):
    scraped_data = scrape_lider(product)
    if scraped_data:
        filename = f'lider_{product}.csv'
        save_to_csv(scraped_data, filename)
        print(f"Se han extraído {len(scraped_data)} productos de {product}")
    else:
        print(f"No se encontraron datos para guardar de la categoría: {product}")

if __name__ == "__main__":
    product = "Verduras"  # Example product category
    run(product)