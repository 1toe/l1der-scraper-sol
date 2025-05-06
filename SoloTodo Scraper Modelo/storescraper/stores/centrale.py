import json
import logging
import re
from decimal import Decimal

import validators
from bs4 import BeautifulSoup

from storescraper.categories import (
    SOLID_STATE_DRIVE,
    EXTERNAL_STORAGE_DRIVE,
    POWER_SUPPLY,
    RAM,
    MOTHERBOARD,
    PROCESSOR,
    VIDEO_CARD,
    NOTEBOOK,
    TABLET,
    MONITOR,
    PRINTER,
    UPS,
    MOUSE,
    KEYBOARD_MOUSE_COMBO,
    COMPUTER_CASE,
    HEADPHONES,
    STEREO_SYSTEM,
    ALL_IN_ONE,
    CELL,
    TELEVISION,
    GAMING_CHAIR,
    KEYBOARD,
    CPU_COOLER,
    STORAGE_DRIVE,
    USB_FLASH_DRIVE,
    MEMORY_CARD,
    CASE_FAN,
    MICROPHONE,
    PRINTER_SUPPLY,
)
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import html_to_markdown, session_with_proxy, remove_words


class Centrale(StoreWithUrlExtensions):
    url_extensions = [
        ["all-in-one-todo-en-uno", ALL_IN_ONE],
        ["audifonos", HEADPHONES],
        ["smartphones", CELL],
        ["kit-teclado-y-mouse", KEYBOARD_MOUSE_COMBO],
        ["refrigeracion-para-pc", CPU_COOLER],
        ["discos-externos", EXTERNAL_STORAGE_DRIVE],
        ["sistemas-de-audio", STEREO_SYSTEM],
        ["pendrive", USB_FLASH_DRIVE],
        ["fuentes-de-poder-para-pc", POWER_SUPPLY],
        ["gabinetes-para-pc", COMPUTER_CASE],
        ["impresoras-tradicionales", PRINTER],
        ["monitores", MONITOR],
        ["mouses", MOUSE],
        ["notebooks", NOTEBOOK],
        ["placas-madres-para-pc", MOTHERBOARD],
        ["procesadores-para-pc", PROCESSOR],
        ["memorias-ram-para-pc", RAM],
        ["memorias-ram-para-servidor", RAM],
        ["sillas-muebles-y-sillas", GAMING_CHAIR],
        ["tablets", TABLET],
        ["tarjetas-micro-sd", MEMORY_CARD],
        ["tarjetas-graficas-para-pc", VIDEO_CARD],
        ["teclados", KEYBOARD],
        ["televisores", TELEVISION],
        ["almacenamiento-para-pc", SOLID_STATE_DRIVE],
        ["ups-sistema-de-alimentacion-ininterrumpida", UPS],
        ["refrigeracion-para-pc", CASE_FAN],
        ["microfonos", MICROPHONE],
        ["suministros-para-impresoras", PRINTER_SUPPLY],
        ["celulares", CELL],
        ["almacenamiento-para-servidor", STORAGE_DRIVE],
        ["parlantes", STEREO_SYSTEM],
        ["pendrives", USB_FLASH_DRIVE],
        ["plotters-gran-formato", PRINTER],
        ["parlantes-para-videoconferencias", STEREO_SYSTEM],
        ["sistemas-integrados-para-videoconferencias", STEREO_SYSTEM],
        ["pantallas-interactivas", MONITOR],
        ["notebooks-gamer", NOTEBOOK],
        ["workstations-portatiles", NOTEBOOK],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args=None):
        session = session_with_proxy(extra_args)
        product_urls = []
        page = 1
        while True:
            if page > 40:
                raise Exception("page overflow: " + url_extension)
            url_webpage = "https://centrale.cl/categoria-producto" "/{}/page/{}".format(
                url_extension, page
            )
            print(url_webpage)
            data = session.get(url_webpage).text
            soup = BeautifulSoup(data, "lxml")
            product_containers = soup.findAll("div", "product-small box")
            if not product_containers:
                if page == 1:
                    logging.warning("Empty category; " + url_webpage)
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
        script_text = soup.findAll("script", {"type": "application/ld+json"})[-1].text
        script_text = re.sub(
            r'(?<=\s)"description":\s".*?"\s*,?', "", script_text, flags=re.DOTALL
        )
        script_text = re.sub(r"\s+", " ", script_text)
        product_data = json.loads(script_text)

        if "@graph" in product_data:
            product_data = product_data["@graph"][-1]

        modified_notebook_parts_label = soup.find("strong", text="COMPONENTES")

        if modified_notebook_parts_label:
            part_number_components = []
            table_tag = modified_notebook_parts_label.parent.find("table")

            for row in table_tag.findAll("tr")[1:]:
                component_mpn = row.findAll("td")[1].text
                part_number_components.append(component_mpn)

            part_number = " + ".join(part_number_components) or None
        else:
            mpn_tag = soup.find("strong", text="NÚMERO DE PARTE:")
            part_number = mpn_tag.next.next.strip()

        sku_tag = soup.find(
            "div",
            {
                "style": "padding-top: 0px; padding-bottom:8px; margin: -12px 0px 0px 0px; text-align: left; font-size: 80%;"
            },
        )
        sku = sku_tag.find("span").text.replace("ID: ", "").strip()
        name = product_data["name"].strip()
        key = soup.find("link", {"rel": "shortlink"})["href"].split("p=")[-1]

        if soup.find("p", "stock in-stock"):
            stock = int(soup.find("p", "stock in-stock").text.split()[0])
        else:
            stock = 0

        offer_price = Decimal(
            remove_words(
                soup.find(
                    "span",
                    {"style": "font-size: 35px; font-weight: 1000; color: #0076F1"},
                ).text.split("$")[1]
            )
        )
        normal_price = Decimal(
            remove_words(
                soup.find(
                    "span",
                    {"style": "font-size: 23px; " "font-weight: bold; color: black;"},
                ).text.split()[0]
            )
        )
        picture_urls = []
        picture_container = soup.find("div", "product-thumbnails")

        if picture_container:
            for tag in picture_container.findAll(
                "img", "attachment-woocommerce_thumbnail"
            ):
                picture_urls.append(tag["src"].replace("-300x300", ""))
        elif soup.find("div", "woocommerce-product-gallery__image"):
            picture_urls.append(
                soup.find("div", "woocommerce-product-gallery__image").find("img")[
                    "src"
                ]
            )

        picture_urls = [x for x in picture_urls if validators.url(x)]
        description = html_to_markdown(soup.find("div", {"id": "tab-description"}).text)

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
            part_number=part_number[:50],
            description=description,
        )
        return [p]
