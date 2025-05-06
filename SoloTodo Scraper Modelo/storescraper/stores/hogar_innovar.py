import json
import re
from decimal import Decimal

from bs4 import BeautifulSoup

from storescraper.categories import TELEVISION
from storescraper.product import Product
from storescraper.store import Store
from storescraper.utils import session_with_proxy


class HogarInnovar(Store):
    @classmethod
    def categories(cls):
        return [TELEVISION]

    @classmethod
    def discover_urls_for_category(cls, category, extra_args=None):
        if category != TELEVISION:
            return []
        session = session_with_proxy(extra_args)
        product_urls = []
        page = 1

        while True:
            if page >= 10:
                raise Exception("Page overflow")

            url = f"https://europe-west1-rapid-product-search.cloudfunctions.net/appV2/api/e5b998-78.myshopify.com/search/?data_index=es_sy4_free_9&engine=shopify&query_id=f08e17eb-014e-4a40-8813-ef937bb13562/1731076020302&max_product_count=30&page={page}&type=resultPage&filter_category_id=296865398895"
            print(url)

            response = session.get(url).json()
            products = response["products"]

            if not products:
                break

            for product in products:
                product_urls.append(f"https://hogarinnovar.com/{product['productUrl']}")

            page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        data = session.get(url).text
        soup = BeautifulSoup(data, "lxml")
        product_data = json.loads(
            soup.findAll("script", {"type": "application/ld+json"})[1].text
        )

        if "hasVariant" in product_data:
            variants = product_data["hasVariant"]

            assert len(variants) == 1

            variant = variants[0]
            offer = variant["offers"]
            name = variant["name"]
        else:
            offer = product_data["offers"]
            name = product_data["name"]

        price = Decimal(offer["price"])

        if price == 0:
            return []

        stock = -1 if offer["availability"] == "http://schema.org/InStock" else 0
        formatted_url = offer["url"]
        regex = r"/products/([^?]+)\?variant=(\d+)"
        match = re.search(regex, formatted_url)
        keywords = [
            "-hd-led-smart-tv",
            "-4k-uhd-nanocell-smart-tv",
            "-4k-uhd-qned-smart-tv",
            "-4k-uhd-led-smart-tv",
            "-4k-uhd-smart-tv",
            "-4k-uhd-oled-smart-tv",
            "4k-uhd-oled-smart-t",
            "-negro",
            "-blanco",
            "-gris",
            "-negra-con-inteligencia-artificial",
            "-8k-smart-tv-con-thinq-ai",
        ]

        for keyword in keywords:
            if keyword in formatted_url:
                url_segments = formatted_url.split(keyword)
                formatted_url = f"{url_segments[0].split('-')[-1]}{url_segments[1]}"
                regex = r"([^?]+)\?variant=(\d+)"
                match = re.search(regex, formatted_url)
                break

        sku = match.group(1)
        key = match.group(2)

        picture_urls = [
            f"https:{img['src'].split('?')[0]}"
            for img in soup.find("product-modal", "product-media-modal").findAll("img")
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
            "COP",
            sku=sku,
            part_number=sku,
            picture_urls=picture_urls,
        )

        return [p]
