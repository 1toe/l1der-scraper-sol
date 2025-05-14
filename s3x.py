import requests
from bs4 import BeautifulSoup

# URL de la página que deseas scrapear
url = 'https://www.unimarc.cl/category/desayuno-y-dulces'

# Realizar la solicitud HTTP a la página
response = requests.get(url)

# Verificar que la solicitud fue exitosa
if response.status_code == 200:
    # Parsear el contenido HTML
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Encontrar todos los contenedores de productos
    product_containers = soup.find_all('div', class_='baseContainer_container__TSgMX baseContainer_justify-start___sjrG baseContainer_align-start__6PKCY baseContainer_flex-direction--column__iiccg baseContainer_absolute-default--topLeft__lN1In')

    # Lista para almacenar la información de los productos
    products = []

    # Iterar sobre cada contenedor de producto
    for container in product_containers:
        # Extraer el nombre del producto
        name = container.find('p', class_='Text_text__cB7NM Shelf_nameProduct__CXI5M').text.strip() if container.find('p', class_='Text_text__cB7NM Shelf_nameProduct__CXI5M') else 'N/A'
        
        # Extraer la marca del producto
        brand = container.find('p', class_='Text_text__cB7NM Shelf_brandText__sGfsS').text.strip() if container.find('p', class_='Text_text__cB7NM Shelf_brandText__sGfsS') else 'N/A'
        
        # Extraer el precio con descuento
        discounted_price = container.find('p', class_='Text_text__cB7NM Text_text--lg__GZWsa Text_text--primary__OoK0C').text.strip() if container.find('p', class_='Text_text__cB7NM Text_text--lg__GZWsa Text_text--primary__OoK0C') else 'N/A'
        
        # Extraer el precio por kilogramo
        price_per_kg = container.find('p', class_='Text_text__cB7NM Text_text--regular__KSs6J Text_text--2xs__QS2Au Text_text--gray-light__DxcpX').text.strip() if container.find('p', class_='Text_text__cB7NM Text_text--regular__KSs6J Text_text--2xs__QS2Au Text_text--gray-light__DxcpX') else 'N/A'
        
        # Extraer el descuento
        discount = container.find('p', class_='Text_text__cB7NM OfferLabel_offerLabel__WrBKB').text.strip() if container.find('p', class_='Text_text__cB7NM OfferLabel_offerLabel__WrBKB') else 'N/A'
        
        # Agregar el producto a la lista
        products.append({
            'name': name,
            'brand': brand,
            'discounted_price': discounted_price,
            'price_per_kg': price_per_kg,
            'discount': discount
        })

    # Imprimir la información de los productos
    for product in products:
        print(product)

else:
    print(f'Error al acceder a la página: {response.status_code}')
    
    
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Configurar Selenium
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# URL de la página que deseas scrapear
url = 'https://www.unimarc.cl/category/desayuno-y-dulces'
driver.get(url)

# Esperar un momento para que la página cargue completamente
time.sleep(5)  # Ajusta el tiempo según sea necesario

# Encontrar todos los contenedores de productos
product_containers = driver.find_elements(By.CLASS_NAME, 'baseContainer_container__TSgMX')

# Lista para almacenar la información de los productos
products = []

# Iterar sobre cada contenedor de producto
for container in product_containers:
    # Extraer el nombre del producto
    name = container.find_element(By.CLASS_NAME, 'Shelf_nameProduct__CXI5M').text.strip() if container.find_elements(By.CLASS_NAME, 'Shelf_nameProduct__CXI5M') else 'N/A'
    
    # Extraer la marca del producto
    brand = container.find_element(By.CLASS_NAME, 'Shelf_brandText__sGfsS').text.strip() if container.find_elements(By.CLASS_NAME, 'Shelf_brandText__sGfsS') else 'N/A'
    
    # Extraer el precio con descuento
    discounted_price = container.find_element(By.CLASS_NAME, 'Text_text--lg__GZWsa').text.strip() if container.find_elements(By.CLASS_NAME, 'Text_text--lg__GZWsa') else 'N/A'
    
    # Extraer el precio por kilogramo
    price_per_kg = container.find_element(By.CLASS_NAME, 'Text_text--regular__KSs6J').text.strip() if container.find_elements(By.CLASS_NAME, 'Text_text--regular__KSs6J') else 'N/A'
    
    # Extraer el descuento
    discount = container.find_element(By.CLASS_NAME, 'OfferLabel_offerLabel__WrBKB').text.strip() if container.find_elements(By.CLASS_NAME, 'OfferLabel_offerLabel__WrBKB') else 'N/A'
    
    # Agregar el producto a la lista
    products.append({
        'name': name,
        'brand': brand,
        'discounted_price': discounted_price,
        'price_per_kg': price_per_kg,
        'discount': discount
    })

# Imprimir la información de los productos
for product in products:
    print(product)

# Cerrar el navegador
driver.quit()