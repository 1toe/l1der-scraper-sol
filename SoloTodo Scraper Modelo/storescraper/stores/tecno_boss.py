from decimal import Decimal
import logging
import json
from bs4 import BeautifulSoup

from storescraper.categories import (
    HEADPHONES,
    MONITOR,
    MOUSE,
    RAM,
    SOLID_STATE_DRIVE,
    VIDEO_CARD,
    PRINTER,
    NOTEBOOK,
    POWER_SUPPLY,
)
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import session_with_proxy


class TecnoBoss(StoreWithUrlExtensions):
    url_extensions = [
        ["notebooks", NOTEBOOK],
        ["todos-los-productos-1/monitor", MONITOR],
        ["mouse-y-teclados", MOUSE],
        ["ssd", SOLID_STATE_DRIVE],
        ["memorias-ram", RAM],
        ["tarjetas-de-video", VIDEO_CARD],
        ["audifonos", HEADPHONES],
        ["todos-los-productos-1/impresoras", PRINTER],
        ["todos-los-productos-1/fuente-de-poder", POWER_SUPPLY],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args=None):
        session = session_with_proxy(extra_args)
        product_urls = []
        page = 1

        while True:
            if page > 10:
                raise Exception(f"Page overflow: {url_extension}")
            url_webpage = f"https://www.tecnoboss.cl/{url_extension}?page={page}"
            print(url_webpage)

            data = session.get(url_webpage).text
            soup = BeautifulSoup(data, "lxml")
            product_containers = soup.find("div", "theme-section__content").findAll(
                "div", "product-block__wrapper"
            )

            if not product_containers:
                if page == 1:
                    logging.warning(f"Empty category: {url_extension}")
                break

            for container in product_containers:
                product_url = container.find("a")["href"]
                product_urls.append(f"https://www.tecnoboss.cl{product_url}")

            page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        response = session.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        product_data = json.loads(soup.find("script", "product-form-json").text)["info"]
        variant = product_data["variant"]

        name = product_data["product"]["name"]
        key = str(variant["id"])
        stock = variant["stock"]
        price = Decimal(variant["price_with_discount"])
        description = soup.find("meta", {"property": "og:description"})["content"]
        picture_urls = [
            picture.find("img")["src"]
            for picture in soup.findAll("picture", "product-gallery__picture")
        ]
        condition = (
            "https://schema.org/RefurbishedCondition"
            if "reacondicionado" in description.lower()
            else "https://schema.org/NewCondition"
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
            condition=condition,
            picture_urls=picture_urls,
            description=description,
        )

        return [p]
