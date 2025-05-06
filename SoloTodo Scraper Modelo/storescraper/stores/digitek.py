import logging
import json
from decimal import Decimal
from bs4 import BeautifulSoup
from storescraper.categories import (
    NOTEBOOK,
    TABLET,
    CELL,
    STEREO_SYSTEM,
    HEADPHONES,
    MOUSE,
    WEARABLE,
    VIDEO_GAME_CONSOLE,
)
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import html_to_markdown, remove_words, session_with_proxy


class Digitek(StoreWithUrlExtensions):
    url_extensions = [
        ["nuevos", CELL],
        ["semi-nuevos", CELL],
        ["macbook", NOTEBOOK],
        ["ipad", TABLET],
        ["applewatch", WEARABLE],
        ["smart-watch", WEARABLE],
        ["smart-band", WEARABLE],
        ["audifonos", HEADPHONES],
        ["parlantes", STEREO_SYSTEM],
        ["computacion", MOUSE],
        ["consolas", VIDEO_GAME_CONSOLE],
        ["outlet", CELL],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args=None):
        session = session_with_proxy(extra_args)
        product_urls = []
        page = 1

        while True:
            url_webpage = f"https://digitek.cl/collections/{url_extension}?page={page}"
            print(url_webpage)

            if page > 10:
                raise Exception("page overflow: " + url_webpage)

            response = session.get(url_webpage)
            soup = BeautifulSoup(response.text, "lxml")
            product_containers = soup.findAll("product-card")

            if not product_containers:
                if page == 1:
                    logging.warning(f"Empty category: {url_extension}")
                break

            for container in product_containers:
                url = container.find("a")["href"]

                if "https://digitek.cl" not in url:
                    url = f"https://digitek.cl{url}"

                product_urls.append(url)

            page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        soup = BeautifulSoup(session.get(url).text, "lxml")
        product_data = json.loads(
            soup.findAll("script", {"type": "application/ld+json"})[2].text
        )
        products = []
        name = product_data["name"]
        description = html_to_markdown(product_data["description"])
        pictures_container = soup.find("media-gallery").findAll("a")
        picture_urls = [f"https:{a['href'].split('?')[0]}" for a in pictures_container]
        product_details = soup.find("div", "product-details").text

        product_texts = [name.lower(), product_details.lower()]
        keywords = {
            "outlet": "https://schema.org/UsedCondition",
            "semi nuevo": "https://schema.org/UsedCondition",
            "seminuevo": "https://schema.org/UsedCondition",
            "semi-nuevos": "https://schema.org/UsedCondition",
            "usada": "https://schema.org/UsedCondition",
            "grado a": "https://schema.org/UsedCondition",
            "grado b": "https://schema.org/UsedCondition",
            "openbox": "https://schema.org/OpenBoxCondition",
            "open box": "https://schema.org/OpenBoxCondition",
        }
        condition = "https://schema.org/NewCondition"

        for keyword, condition_url in keywords.items():
            if any(keyword in text for text in product_texts):
                condition = condition_url
                break

        if "hasVariant" in product_data:
            for variant in product_data["hasVariant"]:
                sku = variant["sku"]
                offer = variant["offers"]
                key = offer["url"].split("?variant=")[1]
                price = Decimal(offer["price"])
                stock = (
                    -1 if offer["availability"] == "http://schema.org/InStock" else 0
                )

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
                    condition=condition,
                    description=description,
                    sku=sku,
                    picture_urls=picture_urls,
                )

                products.append(p)
        else:
            offer = product_data["offers"]
            sku = product_data["sku"]
            offer = product_data["offers"]
            key = offer["url"].split("?variant=")[1]
            price = Decimal(offer["price"])
            stock = -1 if offer["availability"] == "http://schema.org/InStock" else 0

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
                condition=condition,
                description=description,
                sku=sku,
                picture_urls=picture_urls,
            )

            products.append(p)

        return products
