import json
import logging
import urllib
from decimal import Decimal

from bs4 import BeautifulSoup

from storescraper.categories import (
    VIDEO_CARD,
    ALL_IN_ONE,
    NOTEBOOK,
    PROCESSOR,
    MOTHERBOARD,
    SOLID_STATE_DRIVE,
    RAM,
    PRINTER,
    MONITOR,
    MOUSE,
    COMPUTER_CASE,
    EXTERNAL_STORAGE_DRIVE,
    STORAGE_DRIVE,
    TABLET,
    POWER_SUPPLY,
    GAMING_CHAIR,
    CELL,
    TELEVISION,
    UPS,
    HEADPHONES,
    CPU_COOLER,
    VIDEO_GAME_CONSOLE,
    WEARABLE,
    PRINTER_SUPPLY,
)
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import session_with_proxy, remove_words


class TecnoMas(StoreWithUrlExtensions):
    url_extensions = [
        ["Notebooks", NOTEBOOK],
        ["Notebooks Reacondicionados", NOTEBOOK],
        ["Macbook", NOTEBOOK],
        ["Apple", NOTEBOOK],
        ["SSD - Disco Sólido", SOLID_STATE_DRIVE],
        ["HDD - Disco Duros", STORAGE_DRIVE],
        ["Monitores", MONITOR],
        ["Procesadores", PROCESSOR],
        ["Impresoras de Hogar", PRINTER],
        ["Placas Madre", MOTHERBOARD],
        ["Impresoras de Oficina", PRINTER],
        ["Impresoras", PRINTER],
        ["Almacenamiento", SOLID_STATE_DRIVE],
        ["Teclados y Mouse", MOUSE],
        ["Tarjetas de Video", VIDEO_CARD],
        ["All in One (AIO)", ALL_IN_ONE],
        ["AIOs Reacondicionados", ALL_IN_ONE],
        ["PC Oficina", ALL_IN_ONE],
        ["RAM", RAM],
        ["SO-DIMM", RAM],
        ["Gabinetes", COMPUTER_CASE],
        ["Almacenamiento Externo", EXTERNAL_STORAGE_DRIVE],
        ["Tablets", TABLET],
        ["Fuentes de Poder", POWER_SUPPLY],
        ["Celulares", CELL],
        ["Televisores", TELEVISION],
        ["UPS", UPS],
        ["Audio", HEADPHONES],
        ["Ventiladores y Sistemas de Enfriamiento", CPU_COOLER],
        [" Sillas", GAMING_CHAIR],
        ["Consolas", VIDEO_GAME_CONSOLE],
        ["Smartwatch", WEARABLE],
        ["Insumos de Impresora", PRINTER_SUPPLY],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args):
        session = session_with_proxy(extra_args)
        product_urls = []
        page = 0

        while True:
            if page > 35:
                raise Exception("page overflow: " + url_extension)

            facet_filters = urllib.parse.quote(
                json.dumps([["category:{}".format(url_extension)]])
            )

            payload = {
                "requests": [
                    {
                        "indexName": "Product_production",
                        "params": "facetFilters={}&hitsPerPage=48"
                        "&page={}".format(facet_filters, page),
                    }
                ]
            }

            response = session.post(
                "https://wnp9zg9fi5-dsn.algolia.net/1/indexes/*/queries?"
                "x-algolia-api-key=290ed9c571e4c27390d1e57e291379f0&"
                "x-algolia-application-id=WNP9ZG9FI5",
                json=payload,
            )

            json_data = response.json()

            product_containers = json_data["results"][0]["hits"]

            if not product_containers:
                if page == 0:
                    logging.warning("Empty category: " + url_extension)

                break

            for container in product_containers:
                product_urls.append(
                    "https://www.tecnomas.cl/producto/{}".format(container["slug"])
                )

            page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)

        if len(url) > 510:
            return []

        session = session_with_proxy(extra_args)
        session.headers["User-Agent"] = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36"
        )
        response = session.get(url)

        if response.status_code in [404, 500]:
            return []

        soup = BeautifulSoup(response.text, "lxml")
        name = soup.find("h1").text.strip()[:250]
        key = soup.find("input", {"id": "product_id"})["value"]
        sku = soup.find("h2", {"id": "sku-" + key}).text.replace("SKU: ", "").strip()

        stock_text = soup.find("p", {"id": "stock-" + key}).text.strip()
        print(stock_text)

        if "Sin stock" in stock_text or "Agotado" in stock_text:
            stock = 0
        else:
            stock = -1

        if soup.find("span", text="Reacondicionado"):
            condition = "https://schema.org/RefurbishedCondition"
        elif soup.find("span", text="Caja Abierta"):
            condition = "https://schema.org/OpenBoxCondition"
        elif soup.find("span", text="Usado"):
            condition = "https://schema.org/UsedCondition"
        else:
            condition = "https://schema.org/NewCondition"

        offer_price_tag = soup.find("span", {"id": "wire-transfer-price-" + key})
        offer_price = Decimal(remove_words(offer_price_tag.text))

        normal_price_tag = soup.find("span", {"id": "webpay-price-" + key})
        if normal_price_tag:
            normal_price = Decimal(remove_words(normal_price_tag.text))
        else:
            normal_price = offer_price
        slides = soup.findAll("div", "swiper-slide")
        picture_urls = []

        for slide in slides:
            img = slide.find("img")
            if "src" in img.attrs:
                picture_urls.append(img["src"])

        description_tag = soup.find("meta", {"property": "og:description"})
        description = description_tag["content"] if description_tag else None

        if soup.find("span", text="Mejorado"):
            name = f"[MODIFICADO POR TIENDA] {name}"
            part_number = f"[MODIFICADO POR TIENDA] {sku}"
        else:
            part_number = sku

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
            part_number=part_number if len(part_number) < 51 else None,
            picture_urls=picture_urls,
            condition=condition,
            description=description,
        )

        return [p]
