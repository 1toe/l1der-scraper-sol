from bs4 import BeautifulSoup
from decimal import Decimal
import json
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import (
    get_price_from_price_specification,
    session_with_proxy,
    html_to_markdown,
)
from storescraper.categories import (
    CELL,
    NOTEBOOK,
    HEADPHONES,
    MOUSE,
    ACCESORIES,
    VIDEO_GAME_CONSOLE,
    WEARABLE,
)


class TechSaleChile(StoreWithUrlExtensions):
    url_extensions = [
        ["smartphones-y-wearables", CELL],
        ["computadores-y-tablets", NOTEBOOK],
        ["audio-y-video", HEADPHONES],
        ["accesorios-y-perifericos", MOUSE],
        ["hogar-y-seguridad", ACCESORIES],
        ["consolas-y-accesorios", VIDEO_GAME_CONSOLE],
        ["sin-categorizar", WEARABLE],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args):
        product_urls = []
        session = session_with_proxy(extra_args)
        page = 1

        while True:
            url = f"https://techsalechile.cl/categoria-producto/{url_extension}/page/{page}"
            print(url)
            response = session.get(url)

            if response.status_code == 404:
                if page == 1:
                    raise Exception("Invalid section: " + url)
                break

            soup = BeautifulSoup(response.text, "lxml")
            products = soup.findAll("li", "product")

            for product in products:
                product_url = product.find("a")["href"]
                product_urls.append(product_url)

            page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        soup = BeautifulSoup(session.get(url).text, "lxml")
        product_entries = json.loads(
            soup.find("script", {"type": "application/ld+json"}).text
        )

        if "@graph" not in product_entries:
            return []

        for entry in product_entries["@graph"]:
            if entry["@type"] == "Product":
                product_data = entry
                break

        offers = product_data["offers"]
        assert len(offers) == 1

        offer = offers[0]
        name = product_data["name"]
        key = soup.find("link", {"rel": "shortlink"})["href"].split("?p=")[-1]
        stock = 0 if offer["availability"] == "http://schema.org/OutOfStock" else -1
        price = get_price_from_price_specification(product_data)
        sku = str(product_data["sku"])
        description = html_to_markdown(soup.find("div", {"id": "tab-description"}).text)
        image_container = soup.find("div", "woocommerce-product-gallery")
        picture_urls = [a["href"] for a in image_container.findAll("a")]

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
            description=description,
            picture_urls=picture_urls,
        )

        return [p]
