import json
import logging
from decimal import Decimal

from bs4 import BeautifulSoup

from storescraper.categories import (
    HEADPHONES,
    KEYBOARD,
    POWER_SUPPLY,
    COMPUTER_CASE,
    MOUSE,
    CPU_COOLER,
    RAM,
    STEREO_SYSTEM,
    MONITOR,
    GAMING_CHAIR,
    GAMING_DESK,
    SOLID_STATE_DRIVE,
    MICROPHONE,
    NOTEBOOK,
    TELEVISION,
    ACCESORIES,
)
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import session_with_proxy


class VGamers(StoreWithUrlExtensions):
    base_url = "https://vgamers.cl"

    url_extensions = [
        ["perifericos-gamer/audifonos-gamer", HEADPHONES],
        ["perifericos-gamer/teclados-gamer", KEYBOARD],
        ["perifericos-gamer/mouse-gamer", MOUSE],
        ["perifericos-gamer/parlantes", STEREO_SYSTEM],
        ["perifericos-gamer/monitores", MONITOR],
        ["hardware-1/fuentes-de-poder", POWER_SUPPLY],
        ["hardware-1/almacenamiento", SOLID_STATE_DRIVE],
        ["hardware-1/gabinetes-gamer", COMPUTER_CASE],
        ["hardware-1/refrigeracion", CPU_COOLER],
        ["hardware-1/memorias-ram", RAM],
        ["gaming/sillas-gamer", GAMING_CHAIR],
        ["gaming/escritorios-gamer", GAMING_DESK],
        ["hogar-y-oficina/accesorios-computacionales/mouse", MOUSE],
        ["hogar-y-oficina/accesorios-computacionales/teclado", KEYBOARD],
        ["hogar-y-oficina/accesorios-computacionales/audifonos", HEADPHONES],
        ["streaming/microfonos", MICROPHONE],
        ["computadores-y-consolas", NOTEBOOK],
        ["todos-los-productos/televisores", TELEVISION],
        ["electrodomesticos", ACCESORIES],
        ["todos-los-productos/portatiles/notebook", NOTEBOOK],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args=None):
        session = session_with_proxy(extra_args)
        session.headers["User-Agent"] = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36"
        )
        product_urls = []
        page = 1

        while True:
            if page > 10:
                raise Exception("page overflow: " + url_extension)

            url_webpage = f"{cls.base_url}/{url_extension}?page={page}"
            print(url_webpage)

            response = session.get(url_webpage)

            if response.status_code == 404:
                break

            soup = BeautifulSoup(response.text, "lxml")
            products = soup.findAll("article", "product-block")

            if not products:
                if page == 1:
                    logging.warning(f"Empty category: {url_extension}")

                break

            for product in products:
                product_url = product.find("a")["href"]

                if product_url != "/":
                    product_url = f"{cls.base_url}{product_url}"
                    product_urls.append(product_url)

            page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        response = session.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        product_form = soup.find("script", "product-form-json")

        if not product_form:
            return []

        product_data = json.loads(product_form.text)

        json_data = json.loads(
            soup.find("script", {"type": "application/ld+json"}).text
        )
        for entry in json_data:
            if entry["@type"] == "Product":
                json_data = entry
                break
        else:
            raise Exception("No JSON product data found")

        key = str(product_data["info"]["product"]["id"])
        name = product_data["info"]["product"]["name"]
        sku = json_data["sku"]
        description = json_data["description"]
        offer = json_data["offers"]
        price = Decimal(offer["price"])
        stock = product_data["info"]["product"]["stock"]
        picture_urls = [
            slide.find("img")["src"].split("?")[0]
            for slide in soup.findAll("div", "swiper-slide product-gallery__slide")
        ]

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
            picture_urls=picture_urls,
            description=description,
        )
        return [p]
