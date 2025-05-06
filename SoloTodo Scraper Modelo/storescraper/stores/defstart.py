from decimal import Decimal
import json
import logging

from bs4 import BeautifulSoup

from storescraper.categories import (
    WEARABLE,
    HEADPHONES,
    MOUSE,
    STEREO_SYSTEM,
    KEYBOARD,
    CELL,
    SOLID_STATE_DRIVE,
    RAM,
    USB_FLASH_DRIVE,
    PROCESSOR,
    VIDEO_CARD,
    NOTEBOOK,
    ALL_IN_ONE,
    TABLET,
    PRINTER,
    MONITOR,
    UPS,
)
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import (
    get_price_from_price_specification,
    html_to_markdown,
    session_with_proxy,
)


class Defstart(StoreWithUrlExtensions):
    url_extensions = [
        ("apple-watch", WEARABLE),
        ("audifonos", HEADPHONES),
        ("mouse", MOUSE),
        ("parlantes", STEREO_SYSTEM),
        ("smart-watch", WEARABLE),
        ("teclados", KEYBOARD),
        ("celulares", CELL),
        ("disco-duro-partes-y-piezas", SOLID_STATE_DRIVE),
        ("memoria-ram-partes-y-piezas", RAM),
        ("pendrive", USB_FLASH_DRIVE),
        ("procesadores", PROCESSOR),
        ("tarjetas-de-video", VIDEO_CARD),
        ("gamers", NOTEBOOK),
        ("macbook", NOTEBOOK),
        ("notebook", NOTEBOOK),
        ("todo-en-uno", ALL_IN_ONE),
        ("tablet", TABLET),
        ("impresoras-multifuncionales", PRINTER),
        ("monitores", MONITOR),
        ("ups", UPS),
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args=None):
        session = session_with_proxy(extra_args)
        session.headers["user-agent"] = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        )
        product_urls = []
        page = 1

        while True:
            if page > 20:
                raise Exception("Page overflow: " + url_extension)

            url_webpage = f"https://www.defstart.cl/tienda/page/{page}?swoof=1&product_cat={url_extension}"
            print(url_webpage)
            response = session.get(url_webpage)

            if response.status_code == 404:
                if page == 1:
                    logging.warning("Empty category: " + url_extension)
                break

            soup = BeautifulSoup(response.text, "lxml")
            product_containers = soup.findAll("li", "product")

            for container in product_containers:
                product_url = container.findAll("a")[-4]["href"]
                product_urls.append(product_url)

            page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        session.headers["user-agent"] = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        )
        response = session.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        page_data = soup.find("script", {"type": "application/ld+json"}).text
        entries = json.loads(page_data)["@graph"]
        product_data = None
        for entry in entries:
            if entry["@type"] == "Product":
                product_data = entry
                break

        name = product_data["name"]
        sku = str(product_data["sku"])

        offers = product_data["offers"]
        assert len(offers) == 1

        offer = offers[0]
        stock = -1 if offer["availability"] == "http://schema.org/InStock" else 0
        offer_price = get_price_from_price_specification(product_data)
        normal_price = (offer_price * Decimal("1.05")).quantize(0)
        picture_urls = [
            container.find("img")["data-large_image"]
            for container in soup.findAll("div", "woocommerce-product-gallery__image")
        ]
        description = html_to_markdown(soup.find("div", {"id": "tab-description"}).text)
        key = soup.find("link", {"rel": "shortlink"})["href"].split("?p=")[-1]
        condition = (
            "https://schema.org/RefurbishedCondition"
            if "reacondicionado" in name.lower()
            else "https://schema.org/NewCondition"
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
            part_number=sku,
            picture_urls=picture_urls,
            description=description,
            condition=condition,
        )

        return [p]
