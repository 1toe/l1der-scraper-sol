import html
import json
import logging
import re
from decimal import Decimal

import validators
from bs4 import BeautifulSoup

from storescraper.categories import (
    STEREO_SYSTEM,
    MEMORY_CARD,
    USB_FLASH_DRIVE,
    EXTERNAL_STORAGE_DRIVE,
    STORAGE_DRIVE,
    RAM,
    HEADPHONES,
    KEYBOARD,
    MOUSE,
    KEYBOARD_MOUSE_COMBO,
    COMPUTER_CASE,
    MONITOR,
    WEARABLE,
    GAMING_CHAIR,
    CPU_COOLER,
    MOTHERBOARD,
    VIDEO_CARD,
    PROCESSOR,
    POWER_SUPPLY,
    NOTEBOOK,
    TABLET,
    GAMING_DESK,
    MICROPHONE,
    VIDEO_GAME_CONSOLE,
    SOLID_STATE_DRIVE,
    CASE_FAN,
)
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import session_with_proxy


class SipoOnline(StoreWithUrlExtensions):
    url_extensions = [
        ["cooler-cpu", CPU_COOLER],
        ["ventiladores", CASE_FAN],
        ["placa_madres", MOTHERBOARD],
        ["tarjeta_de_video", VIDEO_CARD],
        ["procesadores", PROCESSOR],
        ["fuente_poder", POWER_SUPPLY],
        ["monitor-gamer", MONITOR],
        ["gabinetes", COMPUTER_CASE],
        ["memoria-ram", RAM],
        ["parlante-musica", STEREO_SYSTEM],
        ["memorias", MEMORY_CARD],
        ["pendrives", USB_FLASH_DRIVE],
        ["disco-duro-externo", EXTERNAL_STORAGE_DRIVE],
        ["hdd-disco-duro", STORAGE_DRIVE],
        ["ssd-unidad-estado-solido", SOLID_STATE_DRIVE],
        ["audifonos", HEADPHONES],
        ["parlantes-pc", STEREO_SYSTEM],
        ["audifono-pc", HEADPHONES],
        ["teclado", KEYBOARD],
        ["mouse", MOUSE],
        ["combo-computacion", KEYBOARD_MOUSE_COMBO],
        ["consolas", VIDEO_GAME_CONSOLE],
        ["silla-gamer", GAMING_CHAIR],
        ["audifono-gamer", HEADPHONES],
        ["teclado-gamer", KEYBOARD],
        ["mouse-gamer", MOUSE],
        ["kit-gamer", KEYBOARD_MOUSE_COMBO],
        ["smartwatch", WEARABLE],
        ["notebooks", NOTEBOOK],
        ["tablets", TABLET],
        ["microfono", MICROPHONE],
        ["escritorio-gamer", GAMING_DESK],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args):
        session = session_with_proxy(extra_args)
        session.headers["Cookie"] = "_lscache_vary=a"
        product_urls = []
        page = 1
        while True:
            if page > 10:
                raise Exception("page overflow: " + url_extension)
            url_webpage = (
                "https://sipoonline.cl/product-category/"
                "{}/page/{}/".format(url_extension, page)
            )
            print(url_webpage)
            data = session.get(url_webpage).text
            soup = BeautifulSoup(data, "lxml")
            main = soup.find("main", "site-main")
            if not main:
                if page == 1:
                    logging.warning("Empty category: " + url_extension)
                break
            product_containers = soup.findAll("li", "product")
            for container in product_containers:
                product_url = container.find("a")["href"]
                product_urls.append(product_url)
            page += 1
        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        session.headers["Cookie"] = "_lscache_vary=a"
        response = session.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        product_data = json.loads(
            soup.find("script", {"type": "application/ld+json"}).text
        )

        if "@graph" not in product_data:
            return []

        product_data = product_data["@graph"][1]

        name = product_data["name"]
        sku = str(product_data["sku"])
        description = product_data["description"]
        is_reserva = "VENTA" in description.upper()
        variants = soup.find("form", "variations_form")

        if not variants:
            variants = soup.find("div", "variations_form")

        if variants:
            products = []
            container_products = json.loads(
                html.unescape(variants["data-product_variations"])
            )
            for product in container_products:
                if len(product["attributes"]) > 0:
                    variant_name = (
                        name + " - " + next(iter(product["attributes"].values()))
                    )
                else:
                    variant_name = name
                key = str(product["variation_id"])

                if is_reserva:
                    stock = 0
                elif product["availability_html"] != "":
                    availability_text = BeautifulSoup(
                        product["availability_html"], "lxml"
                    ).text

                    if "Hay existencias" in availability_text:
                        stock = -1
                    else:
                        stock = int(re.search(r"\d+", availability_text).group())
                else:
                    stock = -1
                offer_price = Decimal(product["display_price"])
                normal_price = (offer_price * Decimal("1.05")).quantize(0)
                picture_urls = [product["image"]["src"]]
                p = Product(
                    variant_name,
                    cls.__name__,
                    category,
                    url,
                    url,
                    key,
                    stock,
                    normal_price,
                    offer_price,
                    "CLP",
                    sku=sku,
                    picture_urls=picture_urls,
                    description=description,
                )
                products.append(p)

            return products
        else:
            stock_container = soup.find("p", "stock in-stock")

            if is_reserva:
                stock = 0
            elif stock_container:
                stock_container_text = stock_container.text

                if "Hay existencias" in stock_container_text:
                    stock = -1
                elif "quedan" in stock_container_text:
                    stock = int(re.search(r"\d+", stock_container_text).group())
                else:
                    stock = int(stock_container_text.split()[0])
            elif soup.find("p", "stock out-of-stock"):
                stock = 0
            else:
                stock = -1

            key = soup.find("link", {"rel": "shortlink"})["href"].split("p=")[1]
            offer_price = Decimal(product_data["offers"][0]["price"])
            normal_price = (offer_price * Decimal("1.05")).quantize(0)
            picture_containers = soup.find("ul", "swiper-wrapper").findAll("img")
            picture_urls = [
                tag["src"] for tag in picture_containers if validators.url(tag["src"])
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
                sku=sku,
                picture_urls=picture_urls,
                description=description,
            )

            return [p]
