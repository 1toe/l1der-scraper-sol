import json
import logging

from bs4 import BeautifulSoup
from decimal import Decimal

from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import session_with_proxy, html_to_markdown
from storescraper.categories import (
    SPLIT_AIR_CONDITIONER,
    OVEN,
    VACUUM_CLEANER,
    SPACE_HEATER,
    ACCESORIES,
)


class TiendaToyotomi(StoreWithUrlExtensions):
    url_extensions = [
        ["calefaccion", SPACE_HEATER],
        ["ventilacion/aire-acondicionado", SPLIT_AIR_CONDITIONER],
        ["electrodomesticos", ACCESORIES],
        ["electro-hogar/electrodomesticos/aspiradoras", VACUUM_CLEANER],
        ["electro-hogar/electrodomesticos/hornos-electricos", OVEN],
        ["electro-hogar/electrodomesticos/microondas", OVEN],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args=None):
        session = cls.get_session(extra_args)
        product_urls = []
        page = 1

        while True:
            if page >= 15:
                raise Exception("Page overflow")

            category_url = "https://toyotomi.cl/product-category/{}/" "page/{}".format(
                url_extension, page
            )
            print(category_url)

            soup = BeautifulSoup(session.get(category_url).text, "lxml")

            product_containers = soup.findAll("li", "product")

            if not product_containers:
                if page == 1:
                    logging.warning("Empty path: {}".format(category_url))
                break

            for container in product_containers:
                product_url = container.find("a")["href"]
                product_urls.append(product_url)

            page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        session = cls.get_session(extra_args)
        soup = BeautifulSoup(session.get(url).text, "lxml")

        data = soup.findAll("script", {"type": "application/ld+json"})[-1]

        json_data = json.loads(data.text)

        if "@graph" not in json_data.keys():
            return []

        json_data = json_data["@graph"][1]

        name = json_data["name"]
        sku = str(json_data["sku"])

        price = Decimal(json_data["offers"][0]["price"])

        if json_data["offers"][0]["availability"] in [
            "https://schema.org/InStock",
            "http://schema.org/InStock",
        ]:
            stock = -1
        else:
            stock = 0

        description = json_data["description"]
        description += html_to_markdown(str(soup.find("div", "product_specifications")))

        picture_urls = [x.find("img")["src"] for x in soup.findAll("div", "zoom")]

        p = Product(
            name,
            cls.__name__,
            category,
            url,
            url,
            sku,
            stock,
            price,
            price,
            "CLP",
            sku=sku,
            description=description,
            picture_urls=picture_urls,
        )

        return [p]

    @classmethod
    def get_session(cls, extra_args=None):
        extra_args = extra_args or {}
        extra_args["verify"] = False
        return session_with_proxy(extra_args)
