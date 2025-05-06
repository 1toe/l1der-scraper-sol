import json
from bs4 import BeautifulSoup
from decimal import Decimal
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import (
    session_with_proxy,
    html_to_markdown,
    remove_words,
)
from storescraper.categories import (
    STORAGE_DRIVE,
    SOLID_STATE_DRIVE,
    POWER_SUPPLY,
    COMPUTER_CASE,
    RAM,
    MOTHERBOARD,
    PROCESSOR,
    VIDEO_CARD,
    MONITOR,
    MOUSE,
    KEYBOARD,
)


class Sotecno(StoreWithUrlExtensions):
    url_extensions = [
        ["disco-hdd", STORAGE_DRIVE],
        ["disco-ssd", SOLID_STATE_DRIVE],
        ["fuente-de-poder", POWER_SUPPLY],
        ["gabinete", COMPUTER_CASE],
        ["memoria-ram", RAM],
        ["placa-madre", MOTHERBOARD],
        ["procesador", PROCESSOR],
        ["tarjeta-de-video", VIDEO_CARD],
        ["monitor", MONITOR],
        ["mouse", MOUSE],
        ["teclado", KEYBOARD],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args):
        product_urls = []
        session = session_with_proxy(extra_args)
        page = 1

        while True:
            url = f"https://sotecno.cl/categoria/{url_extension}/page/{page}"
            print(url)
            response = session.get(url)

            if response.status_code == 404:
                if page == 1:
                    raise Exception("Invalid section: " + url)
                break

            soup = BeautifulSoup(response.text, "lxml")
            products = soup.findAll("li", "product")

            if not products:
                break

            for product in products:
                product_url = product.find("a")["href"]
                product_urls.append(product_url)

            page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        response = session.get(url)
        soup = BeautifulSoup(response.text, "lxml")

        key = soup.find("link", {"rel": "shortlink"})["href"].split("=")[-1]
        json_data = json.loads(
            soup.findAll("script", {"type": "application/ld+json"})[-1].text
        )

        for entry in json_data["@graph"]:
            if entry["@type"] == "Product":
                product_data = entry
                break

        assert len(product_data["offers"]) == 1

        offer = product_data["offers"][0]
        name = product_data["name"]
        stock = -1 if offer["availability"] == "http://schema.org/InStock" else 0
        sku = product_data["sku"]
        picture_urls = []
        description = html_to_markdown(soup.find("div", {"id": "tab-description"}).text)
        price_table = soup.find("table", "table-cuota")
        offer_price = Decimal(
            remove_words(
                price_table.find("span", "woocommerce-Price-amount amount").text
            )
        )
        normal_price = Decimal(
            remove_words(
                price_table.findAll("span", "woocommerce-Price-amount amount")[1].text
            )
        )
        picture_urls = [
            container.find("a")["href"]
            for container in soup.findAll("div", "woocommerce-product-gallery__image")
        ]

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
            sku=sku if len(sku) < 51 else None,
            picture_urls=picture_urls,
            description=description,
        )

        return [p]
