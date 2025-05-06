import json
from bs4 import BeautifulSoup
from decimal import Decimal, ROUND_DOWN
from storescraper.categories import TELEVISION

from storescraper.product import Product
from storescraper.store import Store
from storescraper.utils import html_to_markdown, session_with_proxy


class Tata(Store):
    @classmethod
    def categories(cls):
        return [TELEVISION]

    @classmethod
    def discover_urls_for_category(cls, category, extra_args=None):
        if category != TELEVISION:
            return []

        product_urls = []
        session = session_with_proxy(extra_args)
        offset = 0

        while True:
            print(offset)
            payload = {
                "first": 18,
                "after": str(offset),
                "sort": "score_desc",
                "term": "",
                "selectedFacets": [
                    {"key": "brand", "value": "lg"},
                ],
            }

            endpoint = f"https://www.tata.com.uy/api/graphql?operationName=ProductsQuery&variables={json.dumps(payload)}"
            response = session.get(endpoint).json()
            product_entries = response["data"]["search"]["products"]

            if product_entries["edges"] == []:
                break

            for edge in product_entries["edges"]:
                product_urls.append(f"https://www.tata.com.uy/{edge['node']['slug']}/p")

            offset += 18

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        response = session.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        product_data = json.loads(
            soup.findAll("script", {"type": "application/ld+json"})[1].text
        )

        name = product_data["name"]
        sku = product_data["sku"]
        picture_urls = product_data["image"]
        description = product_data["description"]
        offers = product_data["offers"]["offers"]
        products = []
        sellers = {
            "2319": "MultiahorroHogar",
            "2183": "Multiahorro Hogar",
            "1": "Tata",
        }

        for offer in offers:
            seller_id = offer["seller"]["identifier"]
            price = offer["price"]

            if seller_id not in sellers.keys() or price == 0:
                continue

            seller = sellers[seller_id]

            if seller_id == "1":
                currency = "UYU"
                price = Decimal(price).quantize(Decimal("1.00"))
            else:
                price_endpoint = f"https://www.tata.com.uy/api/getMulticurrencyPrices?skuId={sku}&sellerId={seller_id}"
                price_response = session.get(price_endpoint).json()[0]
                discount_value = price_response["discountValue"]
                price = (
                    discount_value
                    if discount_value != "NaN"
                    else price_response["value"]
                )
                currency = "USD"
                price = Decimal(float(price) / 100)

            stock = -1 if offer["availability"] == "https://schema.org/InStock" else 0

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
                currency=currency,
                sku=sku,
                picture_urls=picture_urls,
                description=description,
                seller=seller,
            )

            products.append(p)

        return products
