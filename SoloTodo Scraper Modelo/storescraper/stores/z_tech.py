from bs4 import BeautifulSoup
from decimal import Decimal
import json
import re
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import session_with_proxy, html_to_markdown
from storescraper.categories import KEYBOARD_MOUSE_COMBO, NOTEBOOK, ALL_IN_ONE


class ZTech(StoreWithUrlExtensions):
    url_extensions = [
        ["notebooks-gamers", NOTEBOOK],
        ["notebooks-empresariales", NOTEBOOK],
        ["ultrabooks", NOTEBOOK],
        ["perifericos", KEYBOARD_MOUSE_COMBO],
        ["all-in-one", ALL_IN_ONE],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args):
        product_urls = []
        session = session_with_proxy(extra_args)
        page = 1

        while True:
            if page > 10:
                raise Exception("Page overflow")

            url = f"https://ztech.cl/collections/{url_extension}?page={page}"
            print(url)
            response = session.get(url)
            soup = BeautifulSoup(response.text, "lxml")
            products = soup.findAll("div", "product-card-wrapper")

            if not products:
                break

            for product in products:
                product_urls.append(f"https://ztech.cl{product.find('a')['href']}")

            page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        soup = BeautifulSoup(session.get(url).text, "lxml")
        product_data = json.loads(
            soup.findAll("script", {"type": "application/ld+json"})[1].text
        )
        name = product_data["name"]
        part_number = re.search(r"\[([^]]+)](?!.*\[[^]]+])", name)

        if part_number:
            part_number = part_number.group(1)
        elif category == NOTEBOOK:
            return []

        description = html_to_markdown(product_data["description"])
        picture_urls = [
            f"https:{slide.find('img')['src']}"
            for slide in soup.findAll("div", "product__media media media--transparent")
        ]
        condition = (
            "https://schema.org/RefurbishedCondition"
            if "reacondicionado" in name.lower()
            or "reacondicionado"
            in soup.find(
                "section", "product__info-container product__column-sticky"
            ).text.lower()
            else "https://schema.org/NewCondition"
        )

        if "hasVariant" in product_data:
            products = []

            for variant in product_data["hasVariant"]:
                name = variant["name"]
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
                    part_number=part_number,
                    condition=condition,
                    description=description,
                    picture_urls=picture_urls,
                )

                products.append(p)

            return products
        else:
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
                part_number=part_number,
                condition=condition,
                description=description,
                picture_urls=picture_urls,
            )

            return [p]
