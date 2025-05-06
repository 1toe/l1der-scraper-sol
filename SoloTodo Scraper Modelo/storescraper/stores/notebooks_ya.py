import math
import json
import logging
import re
from decimal import Decimal

from bs4 import BeautifulSoup

from storescraper.categories import (
    NOTEBOOK,
    PRINTER,
    MONITOR,
    HEADPHONES,
    KEYBOARD,
    WEARABLE,
    ALL_IN_ONE,
    TABLET,
    CELL,
    GAMING_CHAIR,
    UPS,
    SOLID_STATE_DRIVE,
    POWER_SUPPLY,
    COMPUTER_CASE,
    RAM,
    PROCESSOR,
    VIDEO_CARD,
    MOTHERBOARD,
    EXTERNAL_STORAGE_DRIVE,
    MOUSE,
    STEREO_SYSTEM,
    VIDEO_GAME_CONSOLE,
    CPU_COOLER,
    PRINTER_SUPPLY,
    PROJECTOR,
)
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import (
    session_with_proxy,
    html_to_markdown,
)


class NotebooksYa(StoreWithUrlExtensions):
    url_extensions = [
        ["apple-watch", WEARABLE],
        ["ipad", TABLET],
        ["imac", ALL_IN_ONE],
        ["macbooks", NOTEBOOK],
        ["accesorios-gamer/?filter_producto-gamer=tarjeta-de-video", VIDEO_CARD],
        [
            "accesorios-gamer/?filter_producto-almacenamiento=tarjeta-de-memoria",
            EXTERNAL_STORAGE_DRIVE,
        ],
        ["audifonos-gamer", HEADPHONES],
        ["monitores-gamer", MONITOR],
        ["portatiles-ya/notebooks-ya/notebooks-gamer", NOTEBOOK],
        ["sillas-gamer", GAMING_CHAIR],
        ["teclados-gamer", KEYBOARD],
        ["notebooks-ya", NOTEBOOK],
        ["tablets", TABLET],
        ["celulares-ya", CELL],
        ["computadores-ya/?filter_producto-computadores=all-in-one", ALL_IN_ONE],
        ["computadores-ya/?filter_producto-computadores=imac", ALL_IN_ONE],
        ["monitores-ya", MONITOR],
        [
            "almacenamiento-ya",
            SOLID_STATE_DRIVE,
        ],
        ["audifonos-ya", HEADPHONES],
        ["teclados-mouse-ya", MOUSE],
        ["relojes-ya", WEARABLE],
        ["sillas-ya", GAMING_CHAIR],
        [
            "partes-y-piezas-ya/?filter_producto-partes-y-piezas=" "fuente-de-poder",
            POWER_SUPPLY,
        ],
        [
            "partes-y-piezas-ya/?filter_producto-partes-y-piezas=gabinetes",
            COMPUTER_CASE,
        ],
        [
            "partes-y-piezas-ya/?filter_producto-partes-y-piezas=memoria-ram-para-laptops",
            RAM,
        ],
        [
            "partes-y-piezas-ya/?filter_producto-partes-y-piezas=memoria-ram-para-pc",
            RAM,
        ],
        [
            "partes-y-piezas-ya/?filter_producto-partes-y-piezas=memoria-para-servidores",
            RAM,
        ],
        [
            "partes-y-piezas-ya/?filter_producto-partes-y-piezas=placa-madre",
            MOTHERBOARD,
        ],
        ["partes-y-piezas-ya/?filter_producto-partes-y-piezas=procesadores", PROCESSOR],
        [
            "partes-y-piezas-ya/?filter_producto-partes-y-piezas=" "tarjeta-de-video",
            VIDEO_CARD,
        ],
        ["impresoras", PRINTER],
        ["audio-y-video-ya/?filter_producto-audio-y-video=audifonos", HEADPHONES],
        [
            "audio-y-video-ya/?filter_producto-audio-y-video=parlante-portatil",
            STEREO_SYSTEM,
        ],
        ["audio-y-video-ya/?filter_producto-audio-y-video=sound-bar", STEREO_SYSTEM],
        ["ups-ya/?filter_producto-ups=ups", UPS],
        ["consolas-y-controles", VIDEO_GAME_CONSOLE],
        [
            "partes-y-piezas-ya/?filter_producto-partes-y-piezas=refrigeracion",
            CPU_COOLER,
        ],
        [
            "insumos-de-impresoras",
            PRINTER_SUPPLY,
        ],
        [
            "proyectores",
            PROJECTOR,
        ],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args):
        session = session_with_proxy(extra_args)
        session.headers["X-Requested-With"] = "XMLHttpRequest"
        product_urls = []
        page = 1
        done = False

        while not done:
            if page > 20:
                raise Exception("page overflow: " + url_extension)

            url_components = url_extension.split("/?")

            if len(url_components) > 1:
                query = url_components[1]
            else:
                query = ""

            url_webpage = f"https://notebooksya.cl/product-category/{url_components[0]}/page/{page}/?load_posts_only=1&{query}"

            print(url_webpage)

            response = session.get(url_webpage)

            if response.status_code == 404:
                if page == 1:
                    logging.warning("Empty category: " + url_extension)
                break

            soup = BeautifulSoup(response.text, "html5lib")
            template_tag = soup.find("script", {"type": "text/template"})

            if template_tag:
                template_soup = BeautifulSoup(json.loads(template_tag.text), "lxml")
                product_containers = template_soup.findAll("li", "product")
            else:
                product_containers = soup.findAll("li", "product")

            if not product_containers:
                if page == 1:
                    logging.warning("Empty category: " + url_extension)
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
        json_data = json.loads(
            soup.findAll("script", {"type": "application/ld+json"})[1].text
        )

        for entry in json_data["@graph"]:
            if entry["@type"] == "Product":
                product_data = entry
                break

        name = product_data["name"]
        assert len(product_data["offers"]) == 1

        offer = product_data["offers"][0]
        key = soup.find("link", {"rel": "shortlink"})["href"].split("?p=")[-1]
        stock = -1 if offer["availability"] == "http://schema.org/InStock" else 0
        gtag = soup.find("script", {"id": "gla-gtag-events-js-extra"})
        gtag_text = re.search(r"var glaGtagData = ({.*?});", gtag.string, re.S).group(1)
        data = json.loads(gtag_text)
        offer_price = Decimal(data["products"][str(key)]["price"])
        normal_price = Decimal(math.ceil(offer_price * Decimal(1.03)))
        sku = str(product_data["sku"])
        picture_urls = [a["href"] for a in soup.findAll("a", "swiper-slide-imglink")]
        description = html_to_markdown(str(soup.find("div", {"id": "tab-description"})))

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
            part_number=sku,
            picture_urls=picture_urls,
            description=description,
        )
        return [p]
