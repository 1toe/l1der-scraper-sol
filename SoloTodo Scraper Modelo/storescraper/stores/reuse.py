import json
import logging
from decimal import Decimal

from bs4 import BeautifulSoup

from storescraper.categories import (
    CELL,
    NOTEBOOK,
    TABLET,
    HEADPHONES,
    WEARABLE,
    KEYBOARD,
    MONITOR,
    TELEVISION,
    REFRIGERATOR,
    VIDEO_GAME_CONSOLE,
    ACCESORIES,
)
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import session_with_proxy, html_to_markdown


class Reuse(StoreWithUrlExtensions):
    url_extensions = [
        ["celulares", CELL],
        ["computadores", NOTEBOOK],
        ["smartwatch", WEARABLE],
        ["tablets", TABLET],
        ["audio-reacondicionado", HEADPHONES],
        ["mouses-y-teclados", KEYBOARD],
        ["monitores-impresoras-y-proyectores", MONITOR],
        ["smart-tv", TELEVISION],
        ["electrodomesticos", REFRIGERATOR],
        ["linea-blanca", REFRIGERATOR],
        ["consolas-y-juegos", VIDEO_GAME_CONSOLE],
        ["electrodomesticos", ACCESORIES],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args=None):
        session = session_with_proxy(extra_args)
        page = 1
        product_urls = []
        while True:
            if page > 20:
                raise Exception("page overflow: " + url_extension)
            url_webpage = "https://www.reuse.cl/collections/" "{}?page={}".format(
                url_extension, page
            )
            print(url_webpage)
            response = session.get(url_webpage)
            soup = BeautifulSoup(response.text, "lxml")
            product_containers = soup.findAll("li", "productgrid--item")
            if not product_containers:
                if page == 1:
                    logging.warning("Empty category: " + url_extension)
                break
            for container in product_containers:
                product_url = container.find("a")["href"]
                product_urls.append("https://www.reuse.cl" + product_url)
            page += 1
        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        response = session.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        product_json = json.loads(
            soup.find(
                "script", {"data-section-id": "template--18401449148633__main"}
            ).text
        )["product"]
        description = html_to_markdown(product_json["description"])
        vendor = product_json["vendor"]
        seller = vendor if vendor != "Reuse Chile" else None

        products = []
        for variant in product_json["variants"]:
            if not variant["inventory_management"]:
                continue

            name = variant["name"]
            sku = variant["sku"]
            key = str(variant["id"])
            stock = -1 if variant["available"] else 0
            price = Decimal(variant["price"] / 100)

            if price > Decimal("100000000"):
                continue

            picture_urls = [
                "https:" + tag.split("?v")[0] for tag in product_json["images"]
            ]
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
                picture_urls=picture_urls,
                condition="https://schema.org/RefurbishedCondition",
                description=description,
                seller=seller,
            )
            products.append(p)

        return products
