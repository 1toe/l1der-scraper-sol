import json

from decimal import Decimal
import time

from storescraper.categories import WASHING_MACHINE
from storescraper.store import Store
from storescraper.product import Product
from storescraper.utils import session_with_proxy


class EVision(Store):
    @classmethod
    def categories(cls):
        return [WASHING_MACHINE]

    @classmethod
    def discover_urls_for_category(cls, category, extra_args=None):
        url_extensions = [WASHING_MACHINE]

        session = session_with_proxy(extra_args)
        session.headers["user-agent"] = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
        )
        session.headers["content-type"] = "text/plain;charset=UTF-8"
        product_urls = []
        payload = '{"keyword": "lg", "apifor": "web"}'

        for local_category in url_extensions:
            if local_category != category:
                continue

            url_webpage = "https://api.evisionstore.com/v1/search-products"
            res = session.post(url_webpage, payload)
            products = json.loads(res.text)["data"]["search_data"]

            for product in products:
                if product["brand"] != "lg":
                    continue

                product_urls.append(
                    "https://www.evisionstore.com/" + product["product_link"]
                )

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        session.headers["user-agent"] = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
        )
        session.headers["content-type"] = "text/plain;charset=UTF-8"
        data = {"model_number": url.split("/")[-1], "source_type": "web"}
        response = session.post(
            "https://api.evisionstore.com/v1/product-detail",
            json.dumps(data),
        )
        response_data = json.loads(response.text)

        if not "data" in response_data:
            return []

        product_data = response_data["data"]["product_view"][0]
        name = product_data["product_name"]
        sku = str(product_data["product_id"])

        if product_data["allow_purchase"] == "0":
            stock = 0
        else:
            stock = -1

        price = Decimal(product_data["price"].replace("$", "").replace(",", "").strip())

        if price == 0:
            return []

        picture_urls = [product_data["product_image"]]
        description = product_data["short_description"].strip()

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
            "USD",
            sku=sku,
            picture_urls=picture_urls,
            description=description,
        )

        return [p]
