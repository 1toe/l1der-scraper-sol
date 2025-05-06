import logging
from decimal import Decimal
import re
from bs4 import BeautifulSoup

from storescraper.categories import (
    CELL,
    STORAGE_DRIVE,
    POWER_SUPPLY,
    COMPUTER_CASE,
    RAM,
    PROCESSOR,
    MOTHERBOARD,
    VIDEO_CARD,
    CPU_COOLER,
    GAMING_CHAIR,
    MONITOR,
    SOLID_STATE_DRIVE,
    MOUSE,
    HEADPHONES,
    KEYBOARD,
    NOTEBOOK,
)
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import html_to_markdown, remove_words, session_with_proxy


class CesaPro(StoreWithUrlExtensions):
    url_extensions = [
        ["accesorios", HEADPHONES],
        ["audio", HEADPHONES],
        ["celulares", CELL],
        ["disco-duro", STORAGE_DRIVE],
        ["solido", SOLID_STATE_DRIVE],
        ["fuentes-de-poder", POWER_SUPPLY],
        ["gabinetes", COMPUTER_CASE],
        ["memoria", RAM],
        ["notebook", RAM],
        ["monitores", MONITOR],
        ["mouse", MOUSE],
        ["placa-madre", MOTHERBOARD],
        ["tarjeta-madre", MOTHERBOARD],
        ["procesadores", PROCESSOR],
        ["sillas", GAMING_CHAIR],
        ["tarjeta-de-video", VIDEO_CARD],
        ["ventilacion", CPU_COOLER],
        ["refrigeracion", CPU_COOLER],
        ["varios", KEYBOARD],
        ["computadores", NOTEBOOK],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args=None):
        session = session_with_proxy(extra_args)
        session.headers["content-type"] = (
            "application/x-www-form-urlencoded;charset=UTF-8"
        )
        session.headers["x-requested-with"] = "XMLHttpRequest"
        product_urls = []

        page = 1

        while True:
            if page > 10:
                raise Exception("page overflow: " + url_extension)

            url_webpage = (
                "https://cesapro.cl/index.php/categoria-produc"
                "to/{}/page/{}/".format(url_extension, page)
            )
            print(url_webpage)
            data = session.get(url_webpage).text
            soup = BeautifulSoup(data, "lxml")
            product_containers = soup.findAll("li", "product")

            if not product_containers:
                if page == 1:
                    logging.warning("empty category: " + url_extension)
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
        response = session.get(url)
        soup = BeautifulSoup(response.text, "lxml")

        key = soup.find("link", {"rel": "shortlink"})["href"].split("?p=")[-1]

        if not soup.find("h1", "product_title"):
            return []

        name = soup.find("h1", "product_title").text.strip()
        product_container = soup.find("p", "price")

        if not product_container.text:
            return []

        if product_container.find("ins"):
            offer_price = Decimal(
                remove_words(
                    product_container.find("ins")
                    .find("span", "woocommerce-Price-amount amount")
                    .text
                )
            )
        else:
            offer_price = Decimal(
                remove_words(
                    product_container.find(
                        "span", "woocommerce-Price-amount " "amount"
                    ).text
                )
            )
        normal_price = (offer_price * Decimal("1.02")).quantize(0)

        stock_span = soup.find("span", "stock")

        if not stock_span:
            stock = 0
        else:
            stock_text = stock_span.text.strip()

            if stock_text == "Agotado":
                stock = 0
            else:
                stock = int(stock_span.text.split(" ")[0])

        image_style = soup.find("style", {"id": "elementor-frontend-inline-css"})
        picture_urls = []

        if image_style:
            picture = re.search(
                r"background-image:url\(\"(.*?)\"\)", image_style.text
            ).groups()[0]
            picture_urls.append(picture)

        description_tag = soup.find("div", {"id": "tab-description"})
        description = (
            html_to_markdown(description_tag.text) if description_tag else None
        )

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
            sku=key,
            picture_urls=picture_urls,
            description=description,
        )

        return [p]
