import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

url = 'https://bff-unimarc-ecommerce.unimarc.cl/catalog/product/nutritional-data/7622201693091'

page = requests.get(url)
soup_jumbo =  BeautifulSoup(page.content, 'html.parser')

# Crear directorio si no existe
output_dir = "Soup Jumbo Resultados"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Generar nombre de archivo con timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = os.path.join(output_dir, f"soup_result_{timestamp}.html")

# Guardar resultado en archivo
with open(output_file, "w", encoding="utf-8") as f:
    f.write(str(soup_jumbo))

print(f"Resultado guardado en: {output_file}")