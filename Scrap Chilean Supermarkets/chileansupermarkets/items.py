# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field

class ProductItem(scrapy.Item):
    # Información básica del producto
    sku = Field()
    name = Field()
    brand = Field()
    price = Field()
    regular_price = Field()
    discount_price = Field()
    discount_percentage = Field()
    
    # Información nutricional y características
    ingredients = Field()
    allergens = Field()
    nutritional_info = Field()
    unit = Field()
    weight = Field()
    
    # Metadata
    url = Field()
    store = Field()
    category = Field()
    subcategory = Field()
    extraction_date = Field()
    image_url = Field()
    
    # Stock
    stock_status = Field()
    stock_quantity = Field()
