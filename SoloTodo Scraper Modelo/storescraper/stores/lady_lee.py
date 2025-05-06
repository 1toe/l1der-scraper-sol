from bs4 import BeautifulSoup
from decimal import Decimal
import json

from storescraper.categories import TELEVISION
from storescraper.product import Product
from storescraper.store import Store
from storescraper.utils import cf_session_with_proxy, html_to_markdown


class LadyLee(Store):

    @classmethod
    def categories(cls):
        return [TELEVISION]

    @classmethod
    def discover_urls_for_category(cls, category, extra_args=None):
        url_extensions = [TELEVISION]

        session = cf_session_with_proxy(extra_args)
        product_urls = []

        for local_category in url_extensions:
            if local_category != category:
                continue
            page = 0
            while True:
                if page > 10:
                    raise Exception("Page overflow")

                url = f"https://ladylee.net/search?type=product&q=lg&page={page}"
                print(url)

                data = session.get(url)
                soup = BeautifulSoup(data.text, "lxml")
                products = soup.find_all("div", "product-item")

                if not products:
                    break

                for product in products:
                    product_urls.append(
                        f"https://ladylee.net/{product.find('a')['href']}"
                    )

                page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = cf_session_with_proxy(extra_args)
        response = session.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        product_data_tag = soup.find("script", {"type": "application/ld+json"})

        if not product_data_tag:
            return []

        product_data = json.loads(product_data_tag.text)
        name = product_data["name"]

        if "sku" not in product_data:
            return []

        sku = product_data["sku"]
        description = html_to_markdown(product_data["description"])
        offer = product_data["offers"]
        variant_id = offer["url"].split("?variant=")[-1]
        price = Decimal(offer["price"])
        stock = -1 if offer["availability"] == "http://schema.org/InStock" else 0
        picture_urls = [product_data["image"].split("?")[0]]

        p = Product(
            name,
            cls.__name__,
            category,
            url,
            url,
            sku,
            stock,
            price,
            price,
            "HNL",
            sku=variant_id,
            picture_urls=picture_urls,
            description=description,
        )

        return [p]
