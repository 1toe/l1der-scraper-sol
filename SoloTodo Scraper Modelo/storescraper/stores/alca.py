from decimal import Decimal
import json
import logging

import validators
from bs4 import BeautifulSoup
from requests import ReadTimeout

from storescraper.categories import (
    PRINTER,
    MOUSE,
    SOLID_STATE_DRIVE,
    ALL_IN_ONE,
    NOTEBOOK,
    MONITOR,
    PRINTER_SUPPLY,
    TABLET,
)
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import get_price_from_price_specification, session_with_proxy


class Alca(StoreWithUrlExtensions):
    url_extensions = [
        ("accesorios", MOUSE),
        ("all-in-one", ALL_IN_ONE),
        ("almacenamiento", SOLID_STATE_DRIVE),
        ("impresoras", PRINTER),
        ("notebooks", NOTEBOOK),
        ("monitores", MONITOR),
        ("suministro", PRINTER_SUPPLY),
        ("tablets", TABLET),
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args=None):
        session = session_with_proxy(extra_args)
        product_urls = []

        page = 1

        while True:
            if page > 80:
                raise Exception("Page overflow: " + url_extension)
            url_webpage = "https://www.alcaplus.cl/solotodo/{}/page/{}/".format(
                url_extension, page
            )

            if url_extension == "suministro":
                url_webpage += "?instock_filter=1"

            print(url_webpage)
            data = session.get(url_webpage).text
            soup = BeautifulSoup(data, "lxml")
            product_containers = soup.findAll("div", "product")

            if not product_containers:
                if page == 1:
                    logging.warning("Empty category: " + url_extension)
                break

            for container in product_containers:
                product_url = container.find("a")["href"]
                product_urls.append(product_url)

            page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)

        try:
            response = session.get(url)
        except ReadTimeout:
            return []

        soup = BeautifulSoup(response.text, "lxml")
        json_data = json.loads(
            soup.findAll("script", {"type": "application/ld+json"})[-1].text
        )
        products = []

        for entry in json_data["@graph"]:
            if entry["@type"] == "Product":
                key_tag = soup.find("link", {"rel": "shortlink"})
                key = key_tag["href"].split("=")[-1]
                product_data = entry
                name = product_data["name"]
                sku = product_data["sku"][:50] if "sku" in product_data else None
                description = product_data["description"]

                assert len(product_data["offers"]) == 1

                price = get_price_from_price_specification(product_data)

                if price == 0:
                    return []

                picture_container = soup.find(
                    "figure", "woocommerce-product-gallery__wrapper"
                )
                picture_urls = [
                    image["href"]
                    for image in picture_container.findAll("a")
                    if validators.url(image["href"])
                ]
                stock_button = soup.find("button", {"name": "add-to-cart"})
                stock = -1 if stock_button else 0

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
                    picture_urls=picture_urls,
                    description=description,
                )
                products.append(p)

                break
        else:
            for product in json.loads(
                soup.find("form", "variations_form")["data-product_variations"]
            ):
                key = str(product["variation_id"])
                name = f"{json_data['@graph'][0]['name']} ({', '.join(product['attributes'].values())})"
                sku = product["sku"][:50]
                description = json_data["@graph"][0]["description"]
                price = Decimal(product["display_price"])
                stock = (
                    0
                    if (product["is_in_stock"] == "False" or not product["max_qty"])
                    else product["max_qty"]
                )
                picture_urls = [product["image"]["url"]]

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
                    picture_urls=picture_urls,
                    description=description,
                )
                products.append(p)

        return products
