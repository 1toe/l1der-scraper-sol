from decimal import Decimal
import json
import logging
from bs4 import BeautifulSoup
from storescraper.categories import (
    HEADPHONES,
    MICROPHONE,
    MONITOR,
    NOTEBOOK,
    PRINTER,
    TABLET,
    TELEVISION,
    WEARABLE,
    USB_FLASH_DRIVE,
    UPS,
    ALL_IN_ONE,
)
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import remove_words, session_with_proxy


class TicOnlineStore(StoreWithUrlExtensions):
    preferred_products_for_url_concurrency = 3

    url_extensions = [
        ["accesorios/categoria-removibles", USB_FLASH_DRIVE],
        ["audiovisual/categoria-audifonos", HEADPHONES],
        ["audiovisual/audio-y-video", HEADPHONES],
        ["audiovisual/categoria-microfono", MICROPHONE],
        ["computacion/categoria-computadores-de-mesa", MONITOR],
        ["computacion/notebook", NOTEBOOK],
        ["computacion/tabletas", TABLET],
        ["computacion/categoria-todo-en-uno", ALL_IN_ONE],
        ["computacion/categoria-ups", UPS],
        ["computacion/categoria-impresoras", PRINTER],
        ["electro/categoria-de-monitores", MONITOR],
        ["electro/televisores", TELEVISION],
        ["wearables", WEARABLE],
        ["zona-gamer", HEADPHONES],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args=None):
        session = session_with_proxy(extra_args)
        session.headers["User-Agent"] = (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
        )
        product_urls = []
        page = 1

        while True:
            if page > 10:
                raise Exception("Page overflow: " + url_extension)
            url_webpage = (
                "https://tic-online-store.cl/categoria-prod"
                "ucto/{}/page/{}".format(url_extension, page)
            )
            data = session.get(url_webpage).text
            soup = BeautifulSoup(data, "lxml")
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
        session.headers["User-Agent"] = (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
        )
        response = session.get(url)
        soup = BeautifulSoup(response.text, "lxml")

        json_data = json.loads(
            soup.findAll("script", {"type": "application/ld+json"})[-1].text
        )

        if "@graph" not in json_data:
            return []

        for entry in json_data["@graph"]:
            if "@type" in entry and entry["@type"] == "Product":
                product_data = entry
                break
        else:
            raise Exception("No JSON product data found")

        name = product_data["name"]
        description = product_data["description"]

        products = []

        if soup.find("form", "variations_form"):
            variations = json.loads(
                soup.find("form", "variations_form")["data-product_variations"]
            )

            for product in variations:
                variation_name = (
                    name + " - " + product["attributes"]["attribute_pa_color"]
                )
                sku = str(product["variation_id"])

                if product["max_qty"] == "":
                    stock = 0
                else:
                    stock = product["max_qty"]

                price = Decimal(product["display_price"])
                picture_urls = [product["image"]["url"]]

                p = Product(
                    variation_name,
                    cls.__name__,
                    category,
                    url,
                    url,
                    sku,
                    stock,
                    price,
                    price,
                    "CLP",
                    sku=sku,
                    picture_urls=picture_urls,
                    description=description,
                )

                products.append(p)
        else:
            key = soup.find("link", {"rel": "shortlink"})["href"].split("?p=")[-1]
            sku = str(product_data["sku"])

            price = Decimal(
                remove_words(soup.find("p", "price").findAll("bdi")[-1].text)
            )

            if len(price.as_tuple().digits) > 10:
                return []

            cart_btn = soup.find("button", {"name": "add-to-cart"})

            if cart_btn:
                input_qty = soup.find("input", "input-text qty text")

                if input_qty:
                    if "max" in input_qty.attrs and input_qty["max"]:
                        stock = int(input_qty["max"])
                    else:
                        stock = -1
                else:
                    stock = 1
            else:
                stock = 0

            picture_urls = []
            container = soup.find("figure", "woocommerce-product-gallery__wrapper")

            if container:
                for a in container.findAll("a"):
                    picture_urls.append(a["href"])
            else:
                picture_urls = None

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
                part_number=sku,
                picture_urls=picture_urls,
                description=description,
            )

            products.append(p)

        return products
