from bs4 import BeautifulSoup
from decimal import Decimal
import json
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import session_with_proxy, html_to_markdown, remove_words
from storescraper.categories import (
    MOTHERBOARD,
    VIDEO_CARD,
    COMPUTER_CASE,
    POWER_SUPPLY,
    CASE_FAN,
    SOLID_STATE_DRIVE,
    RAM,
    MONITOR,
    KEYBOARD,
    EXTERNAL_STORAGE_DRIVE,
    NOTEBOOK,
)


class PlayerPro(StoreWithUrlExtensions):
    url_extensions = [
        ["componentes/placas-madre", MOTHERBOARD],
        ["tarjetas-de-video", VIDEO_CARD],
        ["componentes/gabinetes", COMPUTER_CASE],
        ["componentes/fuentes-de-poder", POWER_SUPPLY],
        ["refrigeracin", CASE_FAN],
        ["componentes/ssd", SOLID_STATE_DRIVE],
        ["componentes/ram", RAM],
        ["monitores", MONITOR],
        ["teclados-y-mouse", KEYBOARD],
        ["almacenamiento-externo", EXTERNAL_STORAGE_DRIVE],
        ["computadores-1/laptops-2-en-1", NOTEBOOK],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args):
        product_urls = []
        session = session_with_proxy(extra_args)
        page = 1

        while True:
            url = f"https://playerpro.cl/{url_extension}?page={page}"
            print(url)
            response = session.get(url)
            soup = BeautifulSoup(response.text, "lxml")
            products = soup.findAll("article", "product-block")

            if not products:
                break

            for product in products:
                status_label = product.find("div", "product-block__label--status")

                if status_label and status_label.text == "Cotizable":
                    continue

                product_url = product.find("a")["href"]
                product_urls.append(f"https://playerpro.cl{product_url}")

            page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        soup = BeautifulSoup(session.get(url).text, "lxml")
        json_data = json.loads(
            soup.find("script", {"type": "application/ld+json"}).text
        )

        for entry in json_data:
            if entry["@type"] == "Product":
                product_data = entry
                break

        if not product_data:
            return []

        name = product_data["name"]
        sku = product_data["sku"]
        key = soup.find("product-price", "product-price")["data-productid"]
        description = html_to_markdown(product_data["description"])
        offer = product_data["offers"]
        offer_price = Decimal(
            remove_words(
                soup.find("p", "price-with-discount").findAll("span")[1].text.strip()
            )
        )
        normal_price = Decimal(offer["price"])

        if normal_price == 0 or offer_price == 0:
            return []

        picture_urls = [
            picture.find("img")["src"]
            for picture in soup.findAll("picture", "product-gallery__picture")
        ]
        type_label = soup.find("div", {"id": "tipo-producto"}).find("b", "oculto")

        if type_label.text not in ["Bodega", "Disponible"]:
            stock = 0
        else:
            stock = -1 if offer["availability"] == "http://schema.org/InStock" else 0

        p = Product(
            name,
            cls.__name__,
            category,
            url,
            url,
            key,
            stock,
            normal_price,
            offer_price,
            "CLP",
            sku=sku,
            description=description,
            picture_urls=picture_urls,
            part_number=sku,
        )

        return [p]
