# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import re
from datetime import datetime
import json


class ChileansupermarketsPipeline:
    def __init__(self):
        self.files = {}

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Limpiar precios
        if adapter.get('price'):
            adapter['price'] = self.clean_price(adapter['price'])
        if adapter.get('regular_price'):
            adapter['regular_price'] = self.clean_price(adapter['regular_price'])
        if adapter.get('discount_price'):
            adapter['discount_price'] = self.clean_price(adapter['discount_price'])
            
        # Limpiar textos
        for field in ['name', 'brand', 'category', 'subcategory']:
            if adapter.get(field):
                adapter[field] = self.clean_text(adapter[field])
                
        # Formatear fecha
        if adapter.get('extraction_date'):
            adapter['extraction_date'] = self.format_date(adapter['extraction_date'])
            
        return item

    def clean_price(self, price):
        """Limpia y normaliza precios"""
        if not price:
            return None
        # Eliminar símbolos de moneda y separadores de miles
        price = re.sub(r'[^\d,.]', '', str(price))
        # Convertir comas a puntos si es necesario
        price = price.replace(',', '.')
        try:
            return float(price)
        except ValueError:
            return None

    def clean_text(self, text):
        """Limpia y normaliza textos"""
        if not text:
            return None
        # Eliminar espacios extras y caracteres especiales
        text = re.sub(r'\s+', ' ', str(text))
        return text.strip()

    def format_date(self, date_str):
        """Formatea fechas al formato ISO"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            return None
