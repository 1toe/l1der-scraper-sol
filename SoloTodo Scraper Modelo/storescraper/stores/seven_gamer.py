import logging
from decimal import Decimal

from bs4 import BeautifulSoup

from storescraper.categories import (
    HEADPHONES,
    CPU_COOLER,
    EXTERNAL_STORAGE_DRIVE,
    POWER_SUPPLY,
    COMPUTER_CASE,
    RAM,
    MONITOR,
    MOUSE,
    MOTHERBOARD,
    PROCESSOR,
    GAMING_CHAIR,
    VIDEO_CARD,
    KEYBOARD,
    GAMING_DESK,
)
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import session_with_proxy, remove_words, html_to_markdown


class SevenGamer(StoreWithUrlExtensions):
    url_extensions = [
        ["audifonos", HEADPHONES],
        ["audifonos-gamer", HEADPHONES],
        ["cooler", CPU_COOLER],
        ["disco-duro", EXTERNAL_STORAGE_DRIVE],
        ["fuente-de-poder", POWER_SUPPLY],
        ["gabinete-gamer", COMPUTER_CASE],
        ["memoria", RAM],
        ["monitor", MONITOR],
        ["mouse", MOUSE],
        ["placa-madre", MOTHERBOARD],
        ["procesador", PROCESSOR],
        ["sillas-gamer", GAMING_CHAIR],
        ["tarjeta-grafica", VIDEO_CARD],
        ["teclado", KEYBOARD],
        ["teclado-gamer", KEYBOARD],
        ["escritorio-gamer", GAMING_DESK],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args):
        session = session_with_proxy(extra_args)
        products_urls = []
        page = 1
        while True:
            if page > 10:
                raise Exception("page overflow: " + url_extension)
            url_webpage = (
                "https://www.7gamer.cl/categoria-producto/{}/"
                "page/{}/".format(url_extension, page)
            )
            data = session.get(url_webpage).text
            soup = BeautifulSoup(data, "lxml")
            product_containers = soup.find("ul", "products")
            if not product_containers or soup.find("div", "info-404"):
                if page == 1:
                    logging.warning("Empty category: " + url_extension)
                break
            for container in product_containers.findAll("li"):
                products_url = container.find("a", "woocommerce-LoopProduct" "-link")[
                    "href"
                ]
                products_urls.append(products_url)
            page += 1
        return products_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        # Append a parameter because the site tends to cache aggresively and
        # keep products "in stock" even if they are actually not available
        response = session.get(url + "?v=2")

        if response.status_code == 404:
            return []

        soup = BeautifulSoup(response.text, "lxml")
        name = soup.find("h1", "product_title").text[0:250]
        sku = soup.find("a", "add-to-compare-link")["data-product_id"]
        if soup.find("p", "out-of-stock") or soup.find("p", "available-on-backorder"):
            stock = 0
        else:
            stock = -1
        if soup.find("p", "price").text == "":
            return []
        if soup.find("p", "price").find("ins"):
            offer_price = Decimal(
                remove_words(soup.find("p", "price").find("ins").text)
            )
        else:
            offer_price = Decimal(remove_words(soup.find("p", "price").text))
        normal_price = (offer_price * Decimal("1.04")).quantize(0)
        picture_urls = [
            tag["src"]
            for tag in soup.find("div", "product-images-wrapper").findAll("img")
        ]
        description = html_to_markdown(str(soup.find("div", {"id": "tab-description"})))
        p = Product(
            name,
            cls.__name__,
            category,
            url,
            url,
            sku,
            stock,
            normal_price,
            offer_price,
            "CLP",
            sku=sku,
            picture_urls=picture_urls,
            description=description,
        )
        return [p]
