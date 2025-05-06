import urllib
from decimal import Decimal
import json
import logging
from bs4 import BeautifulSoup
from storescraper.categories import (
    NOTEBOOK,
    REFRIGERATOR,
    STEREO_SYSTEM,
    TELEVISION,
    SPACE_HEATER,
    HEADPHONES,
    WASHING_MACHINE,
    STOVE,
    KEYBOARD,
    GAMING_CHAIR,
    CELL,
)
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import html_to_markdown, session_with_proxy


class BodegaOportunidades(StoreWithUrlExtensions):
    url_extensions = [
        ["televisores", TELEVISION],
        ["parlantes", STEREO_SYSTEM],
        ["audifonos", HEADPHONES],
        ["computacion", NOTEBOOK],
        ["lavadoras-y-secadoras-1", WASHING_MACHINE],
        ["refrigeradores", REFRIGERATOR],
        ["cocinas", STOVE],
        ["sillas-gamer", GAMING_CHAIR],
        ["teclados-gamer", KEYBOARD],
        ["climatizacion-y-energia", SPACE_HEATER],
        ["telefonos", CELL],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args=None):
        session = session_with_proxy(extra_args)
        session.headers["user-agent"] = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
        )
        product_urls = []
        page = 1
        while True:
            if page > 10:
                raise Exception("Page overflow: " + url_extension)
            url_webpage = (
                "https://bodegaoportunidades.cl/collections/"
                "{}?page={}".format(urllib.parse.quote(url_extension), page)
            )
            print(url_webpage)
            data = session.get(url_webpage).text
            soup = BeautifulSoup(data, "lxml")
            product_containers = soup.findAll("div", "product-item")
            if not product_containers:
                if page == 1:
                    logging.warning("Empty category: " + url_extension)
                break
            for container in product_containers:
                product_url = container.find("a")["href"].split("?")[0]
                product_urls.append("https://bodegaoportunidades.cl" + product_url)
            page += 1
        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        session.headers["user-agent"] = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
        )
        response = session.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        products = []
        products_data = json.loads(
            soup.find("script", {"type": "application/ld+json"}).text
        )
        name = products_data["name"]
        picture_urls = [
            f"https:{img['src']}"
            for img in soup.find("div", "product-gallery__carousel-wrapper").findAll(
                "img"
            )
        ]
        description = html_to_markdown(products_data["description"])
        condition = (
            "https://schema.org/NewCondition"
            if "Estado del producto : Nuevo" in description
            else "https://schema.org/RefurbishedCondition"
        )

        if "hasVariant" in products_data:
            for variant in products_data["hasVariant"]:
                name = variant["name"]
                key = variant["@id"].split("?variant=")[-1].split("#variant")[0]
                sku = variant.get("sku")
                offer = variant["offers"]
                price = Decimal(offer["price"])
                stock = (
                    -1 if offer["availability"] == "http://schema.org/InStock" else 0
                )
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
                    description=description,
                    condition=condition,
                )
                products.append(p)
        else:
            sku = products_data.get("sku", None)
            offer = products_data["offers"]
            key = offer["url"].split("?variant=")[-1].split("#variant")[0]
            price = Decimal(offer["price"])
            stock = -1 if offer["availability"] == "http://schema.org/InStock" else 0
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
                description=description,
                condition=condition,
            )
            products.append(p)

        return products
