from decimal import Decimal
import json
import logging
from bs4 import BeautifulSoup
from storescraper.categories import (
    CELL,
    COMPUTER_CASE,
    CPU_COOLER,
    GAMING_CHAIR,
    HEADPHONES,
    KEYBOARD,
    MONITOR,
    MOTHERBOARD,
    MOUSE,
    NOTEBOOK,
    POWER_SUPPLY,
    PROCESSOR,
    RAM,
    SOLID_STATE_DRIVE,
    STORAGE_DRIVE,
    TABLET,
    VIDEO_CARD,
    EXTERNAL_STORAGE_DRIVE,
    USB_FLASH_DRIVE,
    ALL_IN_ONE,
    KEYBOARD_MOUSE_COMBO,
    STEREO_SYSTEM,
    TELEVISION,
    PRINTER,
    MEMORY_CARD,
    PRINTER_SUPPLY,
    WEARABLE,
)
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import session_with_proxy, remove_words


class Netxa(StoreWithUrlExtensions):
    url_extensions = [
        ["discos-de-estado-solido-externos", EXTERNAL_STORAGE_DRIVE],
        ["discos-de-estado-solido-internos", SOLID_STATE_DRIVE],
        ["discos-duros-externos", EXTERNAL_STORAGE_DRIVE],
        ["discos-duros-internos", STORAGE_DRIVE],
        ["smartphones", CELL],
        ["cajas-gabinetes", COMPUTER_CASE],
        ["fuentes-de-poder", POWER_SUPPLY],
        ["procesadores", PROCESSOR],
        ["tarjetas-de-video", VIDEO_CARD],
        ["tarjetas-madre-placas-madre", MOTHERBOARD],
        ["ventiladores-y-sistemas-de-enfriamiento", CPU_COOLER],
        ["2-en-1", NOTEBOOK],
        ["portatiles", NOTEBOOK],
        ["tablet", TABLET],
        ["todo-en-uno", ALL_IN_ONE],
        ["impresoras-ink-jet", PRINTER],
        ["impresoras-laser", PRINTER],
        ["impresoras-multifuncionales", PRINTER],
        ["modulos-ram-genericos", RAM],
        ["modulos-ram-propietarios", RAM],
        ["tarjetas-de-memoria-flash", MEMORY_CARD],
        ["unidades-flash-usb", USB_FLASH_DRIVE],
        ["sillas", GAMING_CHAIR],
        ["monitores", MONITOR],
        ["televisores", TELEVISION],
        ["auriculares-y-manos-libres", HEADPHONES],
        ["combos-de-teclado-y-raton", KEYBOARD_MOUSE_COMBO],
        ["parlantes-bocinas-cornetas", STEREO_SYSTEM],
        ["ratones", MOUSE],
        ["teclados-y-teclados-de-numeros", KEYBOARD],
        ["cartuchos-de-toner-e-ink-jet", PRINTER_SUPPLY],
        ["smartwatches", WEARABLE],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args=None):
        session = session_with_proxy(extra_args)
        product_urls = []
        page = 1
        while True:
            if page > 30:
                raise Exception("page overflow: " + url_extension)
            url_webpage = "https://netxa.cl/categoria-producto/{}/page/{}/".format(
                url_extension, page
            )
            print(url_webpage)
            response = session.get(url_webpage)

            if response.status_code == 404:
                if page == 1:
                    logging.warning("empty category: " + url_extension)
                break

            soup = BeautifulSoup(response.text, "lxml")
            product_containers = soup.find("ul", "products")

            if not product_containers:
                return []

            product_containers = product_containers.findAll("li", "product")
            for container in product_containers:
                product_url = container.find("a", "woocommerce-LoopProduct-link")[
                    "href"
                ]
                product_urls.append(product_url)
            page += 1
        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        response = session.get(url)
        soup = BeautifulSoup(response.text, "lxml")

        json_data = json.loads(
            soup.find("script", {"type": "application/ld+json"}).text
        )

        if "@graph" not in json_data:
            return []

        for entry in json_data["@graph"]:
            if entry["@type"] == "Product":
                product_data = entry
                break
        else:
            raise Exception("No JSON product data found")

        name = product_data["name"][:250]
        key = soup.find("link", {"rel": "shortlink"})["href"].split("?p=")[-1]
        if product_data["offers"][0]["availability"] == "http://schema.org/InStock":
            stock = -1
        else:
            stock = 0
        sku = product_data["sku"]
        if "image" in product_data:
            picture_urls = [product_data["image"]]
        else:
            picture_urls = None
        description = product_data["description"]

        pricing_tag = soup.find("ul", "custom-prices")

        if pricing_tag:
            price_tags = pricing_tag.findAll("span", "woocommerce-Price-amount")
            assert len(price_tags) == 2
            offer_price = Decimal(remove_words(price_tags[0].text))
            normal_price = Decimal(remove_words(price_tags[1].text))
        else:
            normal_price = offer_price = Decimal(product_data["offers"][0]["price"])

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
            part_number=sku,
        )
        return [p]
