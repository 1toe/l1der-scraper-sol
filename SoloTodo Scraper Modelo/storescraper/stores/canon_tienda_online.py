from bs4 import BeautifulSoup
from decimal import Decimal
import re
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import session_with_proxy, remove_words
from storescraper.categories import PRINTER, PRINTER_SUPPLY


class CanonTiendaOnline(StoreWithUrlExtensions):
    url_extensions = [
        [
            "impresoras-y-multifuncionales",
            PRINTER,
        ],
        [
            "impresoras-y-multifuncionales/impresoras-formato-ancho",
            PRINTER,
        ],
        [
            "impresoras-y-multifuncionales/impresoras-portatiles",
            PRINTER,
        ],
        [
            "impresoras-y-multifuncionales/impresoras-y-multifuncionales-laser",
            PRINTER,
        ],
        [
            "impresoras-y-multifuncionales/impresoras-y-multifuncionales-tinta",
            PRINTER,
        ],
        [
            "tinta-papel-y-toner",
            PRINTER_SUPPLY,
        ],
        [
            "tinta-papel-y-toner/tinta",
            PRINTER_SUPPLY,
        ],
        [
            "tinta-papel-y-toner/toner",
            PRINTER_SUPPLY,
        ],
        [
            "tinta-papel-y-toner/suministros-impresoras-portatiles",
            PRINTER_SUPPLY,
        ],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args):
        product_urls = []
        session = session_with_proxy(extra_args)
        page = 1

        while True:
            if page > 100:
                raise Exception("Page overflow")

            url = f"https://www.canontiendaonline.cl/es_cl/{url_extension}?p={page}"
            print(url)
            response = session.get(url)
            soup = BeautifulSoup(response.text, "lxml")
            products = soup.findAll("div", "product-item-left")

            if not products:
                break

            for product in products:
                product_urls.append(product.find("a", "product")["href"])

            page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        soup = BeautifulSoup(session.get(url).text, "html5lib")

        name = soup.find("span", {"itemprop": "name"}).text
        sku_tag = soup.find("div", {"itemprop": "sku"})
        sku = sku_tag.text if sku_tag else None
        price_tag = soup.find("meta", {"itemprop": "price"})

        if not price_tag:
            return []

        price = Decimal(price_tag["content"])

        if price == 0:
            return []

        key = soup.find("form", {"id": "product_addtocart_form"}).find(
            "input", {"name": "product"}
        )["value"]
        stock = -1 if soup.find("div", "stock available") else 0
        description_tag = soup.find("div", {"itemprop": "description"})
        description = description_tag.text if description_tag else None
        picture_urls = [
            soup.find("img", {"alt": "main product photo"})["src"].replace(" ", "%20")
        ]

        if "DAÑADA" in name.upper():
            condition = "https://schema.org/DamagedCondition"
        else:
            condition = "https://schema.org/NewCondition"

        p = Product(
            name,
            cls.__name__,
            category,
            url,
            url,
            key,
            stock,
            price,
            price,
            "CLP",
            sku=sku,
            part_number=sku,
            description=description,
            picture_urls=picture_urls,
            condition=condition,
        )

        return [p]
