import logging
import json
from decimal import Decimal
from bs4 import BeautifulSoup
from storescraper.categories import (
    COMPUTER_CASE,
    MOTHERBOARD,
    POWER_SUPPLY,
    CPU_COOLER,
    VIDEO_CARD,
    PROCESSOR,
    KEYBOARD,
    RAM,
    MOUSE,
    HEADPHONES,
    MONITOR,
    SOLID_STATE_DRIVE,
)
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import get_price_from_price_specification, session_with_proxy


class EvoPc(StoreWithUrlExtensions):
    url_extensions = [
        ["gabinetes", COMPUTER_CASE],
        ["placas-madres", MOTHERBOARD],
        ["fuentes-de-poder", POWER_SUPPLY],
        ["refrigeracion", CPU_COOLER],
        ["tarjetas-de-video", VIDEO_CARD],
        ["procesadores", PROCESSOR],
        ["memorias-ram", RAM],
        ["teclados", KEYBOARD],
        ["audifonos", HEADPHONES],
        ["monitor", MONITOR],
        ["mouse", MOUSE],
        ["almacenamiento", SOLID_STATE_DRIVE],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args=None):
        session = session_with_proxy(extra_args)
        session.headers = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        }
        product_urls = []
        page = 1

        while True:
            url_webpage = (
                f"https://evopc.cl/product-category/{url_extension}/page/{page}/"
            )
            print(url_webpage)

            if page > 10:
                raise Exception("page overflow: " + url_webpage)

            response = session.get(url_webpage)
            soup = BeautifulSoup(response.text, "lxml")
            product_containers = soup.findAll("li", "product")

            if response.status_code == 404:
                if page == 1:
                    logging.warning(f"Empty category: {url_extension}")
                break

            for container in product_containers:
                product_urls.append(container.find("a")["href"])

            page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        soup = BeautifulSoup(session.get(url).text, "lxml")
        page_data = json.loads(
            soup.find("script", {"type": "application/ld+json"}).text
        )
        product_data = None

        if "@graph" not in page_data:
            return []

        for data in page_data["@graph"]:
            if data["@type"] == "Product":
                product_data = data

        assert len(product_data["offers"]) == 1

        name = product_data["name"]
        offer = product_data["offers"][0]
        sku = product_data["sku"]
        sku = sku if len(sku) <= 50 else None
        key_tag = soup.find("button", {"name": "add-to-cart"})

        if key_tag:
            key = key_tag["value"]
        else:
            canonical_url_tag = soup.find(
                "link", {"rel": "alternate", "type": "application/json"}
            )
            key = canonical_url_tag["href"].split("/")[-1]

        offer_price = get_price_from_price_specification(product_data)
        price = (offer_price * Decimal(1.04)).quantize(0)
        stock = -1 if offer["availability"] == "http://schema.org/InStock" else 0
        picture_urls = [
            a["href"]
            for a in soup.find("div", "woocommerce-product-gallery__wrapper").findAll(
                "a"
            )
        ]
        description = product_data["description"]

        p = Product(
            name,
            cls.__name__,
            category,
            url,
            url,
            key,
            stock,
            price,
            offer_price,
            "CLP",
            description=description,
            sku=sku,
            picture_urls=picture_urls,
        )

        return [p]
