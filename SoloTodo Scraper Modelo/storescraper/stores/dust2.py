import re
from bs4 import BeautifulSoup
from decimal import Decimal
from storescraper.categories import (
    PRINTER,
    UPS,
    MOUSE,
    KEYBOARD,
    HEADPHONES,
    STEREO_SYSTEM,
    GAMING_CHAIR,
    COMPUTER_CASE,
    CPU_COOLER,
    RAM,
    POWER_SUPPLY,
    PROCESSOR,
    MOTHERBOARD,
    VIDEO_CARD,
    STORAGE_DRIVE,
    MEMORY_CARD,
    EXTERNAL_STORAGE_DRIVE,
    USB_FLASH_DRIVE,
    MONITOR,
    KEYBOARD_MOUSE_COMBO,
    NOTEBOOK,
    WEARABLE,
    SOLID_STATE_DRIVE,
    CASE_FAN,
    ALL_IN_ONE,
    TABLET,
)
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import html_to_markdown, remove_words, session_with_proxy


class Dust2(StoreWithUrlExtensions):
    url_extensions = [
        ["teclados-gamer", KEYBOARD],
        ["mouse-gamer", MOUSE],
        ["audifonos-gamer", HEADPHONES],
        ["sillas-gamer", GAMING_CHAIR],
        ["kits-gamer", KEYBOARD_MOUSE_COMBO],
        ["parlantes-gamer", STEREO_SYSTEM],
        ["monitores-gamer", MONITOR],
        ["monitores", MONITOR],
        ["procesadores", PROCESSOR],
        ["tarjetas-de-video", VIDEO_CARD],
        ["placas-madres", MOTHERBOARD],
        ["fuentes-de-poder", POWER_SUPPLY],
        ["gabinetes", COMPUTER_CASE],
        ["memorias-ram", RAM],
        ["refrigeracion-liquida", CPU_COOLER],
        ["fans-y-controladores", CASE_FAN],
        ["cooler-para-cpu", CPU_COOLER],
        ["discos-m-2", SOLID_STATE_DRIVE],
        ["ssd-y-discos-duros", STORAGE_DRIVE],
        ["discos-y-ssd-externos", EXTERNAL_STORAGE_DRIVE],
        ["audifonos-xbox", HEADPHONES],
        ["impresoras", PRINTER],
        ["respaldo-energia", UPS],
        ["smartband", WEARABLE],
        ["pendrives", USB_FLASH_DRIVE],
        ["accesorios-tablets", TABLET],
        ["notebooks", NOTEBOOK],
        ["equipos", NOTEBOOK],
        ["memorias-ram-notebooks", RAM],
        ["teclados-perifericos", KEYBOARD],
        ["mouse-perifericos", MOUSE],
        ["audifonos-audio", HEADPHONES],
        ["parlantes-audio", STEREO_SYSTEM],
        ["combo-teclado-y-mouse", KEYBOARD_MOUSE_COMBO],
        ["aio", ALL_IN_ONE],
        ["tarjetas-de-memoria", MEMORY_CARD],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args):
        session = session_with_proxy(extra_args)
        page = 1
        product_urls = []

        while True:
            url = f"https://dust2.gg/categoria-producto/{url_extension}/page/{page}/"
            print(url)
            response = session.get(url)

            if response.status_code == 404:
                break

            soup = BeautifulSoup(response.text, "lxml")
            products = soup.find_all("div", "productCard")

            for product in products:
                product_urls.append(product.find("a", "product-link")["href"])

            page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        response = session.get(url)
        soup = BeautifulSoup(response.text, "lxml")

        name = soup.find(
            "div", "Content__singleProduct--right-productName"
        ).text.strip()
        key = soup.find("link", {"rel": "shortlink"})["href"].split("?p=")[-1]
        stock = (
            0 if soup.find("div", "out-of-stock") or "preventa" in name.lower() else -1
        )
        offer_price = Decimal(
            remove_words(
                soup.find("div", "singleProduct__right--productPrice-cash").text
            )
        )
        normal_price = Decimal(
            remove_words(
                soup.find("div", "singleProduct__right--productPrice-card").text
            )
        )
        sku = (
            soup.find("div", "Content__singleProduct--right-productSKU")
            .find("span")
            .text.strip()
        )
        picture_urls = [
            slide.find("img")["src"]
            for slide in soup.find_all("div", "zoomProductImage_slider-slide")
        ]

        description = html_to_markdown(
            soup.find("div", "Content__reportError--body-description").text
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
            sku=sku,
            picture_urls=picture_urls if picture_urls != [""] else None,
            description=description,
        )

        return [p]
