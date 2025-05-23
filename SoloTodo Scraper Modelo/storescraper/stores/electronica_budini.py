import json
import logging
from decimal import Decimal

from bs4 import BeautifulSoup

from storescraper.categories import (
    CELL,
    GAMING_DESK,
    PRINTER,
    SOLID_STATE_DRIVE,
    STORAGE_DRIVE,
    POWER_SUPPLY,
    COMPUTER_CASE,
    RAM,
    MONITOR,
    MOUSE,
    MOTHERBOARD,
    NOTEBOOK,
    PROCESSOR,
    USB_FLASH_DRIVE,
    VIDEO_CARD,
    GAMING_CHAIR,
    CPU_COOLER,
    ALL_IN_ONE,
    HEADPHONES,
    EXTERNAL_STORAGE_DRIVE,
    TABLET,
    KEYBOARD_MOUSE_COMBO,
    KEYBOARD,
    VIDEO_GAME_CONSOLE,
)
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import (
    get_price_from_price_specification,
    html_to_markdown,
    session_with_proxy,
)


class ElectronicaBudini(StoreWithUrlExtensions):
    url_extensions = [
        ["audio", HEADPHONES],
        ["combo-teclado-mouse", KEYBOARD_MOUSE_COMBO],
        ["disco-duro-externo", EXTERNAL_STORAGE_DRIVE],
        ["discos-de-estado-solido-ssd", SOLID_STATE_DRIVE],
        ["discos-duros-hdd", STORAGE_DRIVE],
        ["fuentes-de-poder", POWER_SUPPLY],
        ["gabinetes-gamer", COMPUTER_CASE],
        ["memorias-ram/memoria-ram-notebook", RAM],
        ["memorias-ram/memoria-ram-pc", RAM],
        ["monitores", MONITOR],
        ["mouse-gamer", MOUSE],
        ["notebooks", NOTEBOOK],
        ["placas-madre-amd-ryzen", MOTHERBOARD],
        ["placas-madre-intel", MOTHERBOARD],
        ["procesadores", PROCESSOR],
        ["silla-gamer", GAMING_CHAIR],
        ["escritorio-gamer", GAMING_DESK],
        ["tarjetas-de-video", VIDEO_CARD],
        ["teclado-gamer", KEYBOARD],
        ["todo-en-uno-aio", ALL_IN_ONE],
        ["ventiladores-y-sistemas-de-enfriamiento", CPU_COOLER],
        ["consola", VIDEO_GAME_CONSOLE],
        ["pendrive", USB_FLASH_DRIVE],
        ["tablet", TABLET],
        ["impresoras", PRINTER],
        ["celulares", CELL],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args=None):
        session = session_with_proxy(extra_args)
        session.headers["user-agent"] = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
        )
        product_urls = []
        page = 1
        while True:
            if page > 10:
                raise Exception("page overflow: " + url_extension)

            url_webpage = (
                "https://electronicabudini.cl/categoria-prod"
                "ucto/{}/page/{}/".format(url_extension, page)
            )
            print(url_webpage)
            data = session.get(url_webpage).text
            soup = BeautifulSoup(data, "html5lib")
            product_containers = soup.find("ul", "products")

            if not product_containers or soup.find("div", "error-404"):
                if page == 1:
                    logging.warning("Empty category: " + url_extension)
                break
            for container in product_containers.findAll("li", "product"):
                product_url = container.find("a")["href"]
                if "categoria-producto" in product_url:
                    continue
                product_urls.append(product_url)
            page += 1
        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        session.headers["user-agent"] = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
        )
        response = session.get(url)
        soup = BeautifulSoup(response.text, "lxml")

        json_data = json.loads(
            soup.findAll("script", {"type": "application/ld+json"})[1].text
        )
        product_data = json_data["@graph"][1]
        name = product_data["name"]
        sku = str(product_data["sku"])
        offer_price = get_price_from_price_specification(product_data)
        normal_price = (offer_price * Decimal("1.04")).quantize(0)

        if soup.find("button", {"name": "add-to-cart"}):
            stock = -1
        else:
            stock = 0

        picture_urls = [
            tag["src"]
            for tag in soup.find("div", "woocommerce-product-gallery").findAll("img")
        ]

        refurbished_keywords = ["OPEN BOX", "SEMI", "EXHIBICION", "USADO"]

        condition = "https://schema.org/NewCondition"

        for kw in refurbished_keywords:
            if kw in name.upper():
                condition = "https://schema.org/RefurbishedCondition"

        description = html_to_markdown(soup.find("div", {"id": "tab-description"}).text)

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
            condition=condition,
            description=description,
        )
        return [p]
