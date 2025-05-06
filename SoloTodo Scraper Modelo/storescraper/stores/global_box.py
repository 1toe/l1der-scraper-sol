import logging
import json
from decimal import Decimal

from bs4 import BeautifulSoup

from storescraper.categories import (
    MOTHERBOARD,
    POWER_SUPPLY,
    PROCESSOR,
    VIDEO_CARD,
    NOTEBOOK,
    TABLET,
    ALL_IN_ONE,
    RAM,
    USB_FLASH_DRIVE,
    EXTERNAL_STORAGE_DRIVE,
    STORAGE_DRIVE,
    SOLID_STATE_DRIVE,
    KEYBOARD_MOUSE_COMBO,
    MONITOR,
    PRINTER,
    CELL,
    STEREO_SYSTEM,
    HEADPHONES,
    GAMING_CHAIR,
    COMPUTER_CASE,
    KEYBOARD,
    MOUSE,
    UPS,
    WEARABLE,
    CPU_COOLER,
    MEMORY_CARD,
    TELEVISION,
    CASE_FAN,
    VIDEO_GAME_CONSOLE,
    PRINTER_SUPPLY,
)
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import html_to_markdown, remove_words, session_with_proxy


class Globalbox(StoreWithUrlExtensions):
    url_extensions = [
        ["notebooks", NOTEBOOK],
        ["all-in-one", ALL_IN_ONE],
        ["tablets", TABLET],
        ["macbook", NOTEBOOK],
        ["imac", ALL_IN_ONE],
        ["ipad", TABLET],
        ["monitores", MONITOR],
        ["mouse", MOUSE],
        ["teclados", KEYBOARD],
        ["combo-teclado-y-mouse", KEYBOARD_MOUSE_COMBO],
        ["parlantes-de-pc", STEREO_SYSTEM],
        ["auriculares-y-headset", HEADPHONES],
        ["memorias-ram", RAM],
        ["unidades-flash", USB_FLASH_DRIVE],
        ["tarjetas-de-memoria", MEMORY_CARD],
        ["discos-duros-externos", EXTERNAL_STORAGE_DRIVE],
        ["discos-duros-internos", STORAGE_DRIVE],
        ["unidades-de-estado-solido", SOLID_STATE_DRIVE],
        ["unidades-de-estado-solido-externos", EXTERNAL_STORAGE_DRIVE],
        ["tarjetas-graficas", VIDEO_CARD],
        ["torres", COMPUTER_CASE],
        ["ventiladores-pc", CASE_FAN],
        ["refrigeracion-cpu", CPU_COOLER],
        ["procesadores", PROCESSOR],
        ["placas-base", MOTHERBOARD],
        ["fuentes-de-alimentacion", POWER_SUPPLY],
        ["ups-y-respaldo-energia", UPS],
        ["impresoras-laser", PRINTER],
        ["impresoras-tinta", PRINTER],
        ["impresoras-multifuncionales", PRINTER],
        ["impresoras-laser", PRINTER],
        ["celulares", CELL],
        ["smartwatches", WEARABLE],
        ["wearables", WEARABLE],
        ["smart-tv", TELEVISION],
        ["parlantes", STEREO_SYSTEM],
        ["monitores-de-estudio", STEREO_SYSTEM],
        ["barras-de-sonido", STEREO_SYSTEM],
        ["consolas-de-videojuegos", VIDEO_GAME_CONSOLE],
        ["sillas-y-escritorios-gaming", GAMING_CHAIR],
        ["tintas-de-impresora", PRINTER_SUPPLY],
        ["toner-de-impresora", PRINTER_SUPPLY],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args=None):
        session = session_with_proxy(extra_args)
        session.headers["user-agent"] = "SoloTodoBot"
        product_urls = []
        page = 1

        while True:
            url_webpage = (
                f"https://globalbox.cl/categoria-producto/{url_extension}/page/{page}/"
            )
            print(url_webpage)

            if page > 10:
                raise Exception("page overflow: " + url_webpage)

            response = session.get(url_webpage, allow_redirects=True)

            if response.url == "https://globalbox.cl/":
                if page == 1:
                    logging.warning(f"Empty category: {url_extension}")
                break

            soup = BeautifulSoup(response.text, "lxml")
            product_containers = soup.findAll("li", "product")

            for container in product_containers:
                product_urls.append(
                    container.find("a", "woocommerce-loop-product__link")["href"]
                )

            page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        session.headers["user-agent"] = "SoloTodoBot"
        response = session.get(url)
        soup = BeautifulSoup(response.text, "lxml")

        product_data = None
        json_data = json.loads(
            soup.findAll("script", {"type": "application/ld+json"})[0].text
        )

        for entry in json_data["@graph"]:
            if entry["@type"] == "Product":
                product_data = entry
                break

        name = product_data["name"]
        key = soup.find("link", {"rel": "shortlink"})["href"].split("?p=")[-1]
        sku = product_data["sku"]
        offer = product_data["offers"]
        price = Decimal(offer["price"])
        stock = -1 if offer["availability"] == "https://schema.org/InStock" else 0
        picture_urls = [soup.find("div", "single-product-wrapper").find("a")["href"]]
        description = soup.find("div", {"id": "tab-specification"})

        if not description:
            description = soup.find(
                "div", "woocommerce-product-details__short-description"
            )

        description = html_to_markdown(description.text) if description else None

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
            description=description,
            sku=sku,
            part_number=sku,
            picture_urls=picture_urls,
        )

        return [p]
