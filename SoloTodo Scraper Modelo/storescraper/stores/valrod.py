import logging
import re
from decimal import Decimal

from bs4 import BeautifulSoup

from storescraper.categories import (
    CASE_FAN,
    HEADPHONES,
    GAMING_CHAIR,
    KEYBOARD,
    MICROPHONE,
    MONITOR,
    COMPUTER_CASE,
    MOUSE,
    ACCESORIES,
    POWER_SUPPLY,
    CPU_COOLER,
)
from storescraper.product import Product
from storescraper.store import Store
from storescraper.utils import html_to_markdown, session_with_proxy, remove_words


class Valrod(Store):
    @classmethod
    def categories(cls):
        return [
            GAMING_CHAIR,
            COMPUTER_CASE,
            MONITOR,
            POWER_SUPPLY,
            CPU_COOLER,
            CASE_FAN,
            MOUSE,
            KEYBOARD,
            HEADPHONES,
            MICROPHONE,
            ACCESORIES,
        ]

    @classmethod
    def discover_urls_for_category(cls, category, extra_args=None):
        url_extensions = [
            ["sillas-y-sofas", GAMING_CHAIR],
            ["gabinetes", COMPUTER_CASE],
            ["monitores", MONITOR],
            ["hardware/fuentes-de-poder", POWER_SUPPLY],
            ["hardware/disipadores", CPU_COOLER],
            ["enfriadores-liquidos", CPU_COOLER],
            ["hardware/ventiladores", CASE_FAN],
            ["perifericos-y-accesorios/mouse-y-mousepads", MOUSE],
            ["perifericos-y-accesorios/teclados", KEYBOARD],
            ["perifericos-y-accesorios/audifonos", HEADPHONES],
            ["perifericos-y-accesorios/accesorios", MICROPHONE],
            ["hogar/cocina", ACCESORIES],
        ]
        session = session_with_proxy(extra_args)
        product_urls = []

        for url_extension, local_category in url_extensions:
            if local_category != category:
                continue

            page = 1

            while True:
                if page > 10:
                    raise Exception("page overflow: " + url_extension)

                url_webpage = "https://valrod.cl/{}?page={}".format(url_extension, page)
                print(url_webpage)
                response = session.get(url_webpage)
                soup = BeautifulSoup(response.text, "lxml")
                product_container = soup.findAll("div", "product-item large")

                if not product_container:
                    if page == 1:
                        logging.warning("Empty category: " + url_extension)

                    break

                for container in product_container:
                    product_url = container.find("a")["href"]
                    product_urls.append("https://valrod.cl" + product_url)

                page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        response = session.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        name = soup.find("div", "product-name-wrapper").find("h1").text
        key = soup.find("form", {"id": "addtocart"})["action"].split("/")[-1]

        sku_match = re.search(r'"sku":\s?"(.+?)"', response.text)

        if sku_match:
            sku = sku_match.groups()[0]
        else:
            sku = None

        stock_container = soup.find("div", "product-availability").find("span")

        if stock_container.text == "No Disponible" or stock_container.text == "Agotado":
            stock = 0
        else:
            stock = int(stock_container.text)

        price = Decimal(
            remove_words(soup.find("div", "price").find("span", "special-price").text)
        )
        picture_urls = [
            tag["src"].split("?")[0]
            for tag in soup.find("div", "product-previews-wrapper").findAll("img")
        ]

        if "CAJA ABIERTA" in name.upper():
            condition = "https://schema.org/RefurbishedCondition"
        else:
            condition = "https://schema.org/NewCondition"

        description = html_to_markdown(
            soup.find("div", {"id": "product-description"}).text
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
            part_number=sku,
            picture_urls=picture_urls,
            condition=condition,
            description=description,
        )

        return [p]
