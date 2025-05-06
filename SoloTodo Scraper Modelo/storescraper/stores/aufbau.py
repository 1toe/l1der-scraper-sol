from decimal import Decimal
import json

from storescraper.categories import (
    ALL_IN_ONE,
    CELL,
    HEADPHONES,
    NOTEBOOK,
    TABLET,
    WEARABLE,
    VIDEO_GAME_CONSOLE,
)
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import remove_words, session_with_proxy, html_to_markdown


class Aufbau(StoreWithUrlExtensions):
    url_extensions = [
        ["macbook-air", NOTEBOOK],
        ["macbook-pro", NOTEBOOK],
        ["imac", ALL_IN_ONE],
        ["ipad-pro", TABLET],
        ["ipad-air", TABLET],
        ["ipad", TABLET],
        ["ipad-mini", TABLET],
        ["iphone-se", CELL],
        ["iphone-16-pro", CELL],
        ["iphone-16", CELL],
        ["iphone-15-pro", CELL],
        ["iphone-15", CELL],
        ["iphone-14", CELL],
        ["iphone-13", CELL],
        ["apple-watch-ultra-2", WEARABLE],
        ["apple-watch-series-10", WEARABLE],
        ["apple-watch-series-9", WEARABLE],
        ["apple-watch-1", WEARABLE],
        ["airpods-pro", HEADPHONES],
        ["airpods", HEADPHONES],
        ["airpods-max", HEADPHONES],
        ["beats", HEADPHONES],
        ["parlantes-audifonos", HEADPHONES],
        ["gaming", VIDEO_GAME_CONSOLE],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args=None):
        session = session_with_proxy(extra_args)
        session.headers["origin"] = "https://aufbau.cl"
        product_urls = []
        page = 0

        while True:
            url_webpage = f"https://api-prd.ynk.cl/rest/v2/reifstoreb2cstore/cms/pages?pageLabelOrId=%2Fcollections%2F{url_extension}"
            response = json.loads(session.get(url_webpage).text)

            if "contentSlots" in response:
                print(url_webpage)
                contentSlots = response["contentSlots"]
                product_grids = None

                for slot in contentSlots:
                    for component in contentSlots[slot]:
                        for entry in component["components"]["component"]:
                            if entry["typeCode"] == "ProductGrid":
                                product_grids = entry["gridItems"].replace(" ", "%2C")

                products_url = f"https://api-prd.ynk.cl/rest/v2/reifstoreb2cstore/cms/components?currentPage={page}&pageSize=18&componentIds={product_grids}"
                product_containers = json.loads(session.get(products_url).text)[
                    "component"
                ]

                if not product_containers:
                    break

                for container in product_containers:
                    product_urls.append(
                        f"https://www.aufbau.cl{container['buttonLink']}"
                    )

            else:
                products_url = f"https://api-prd.ynk.cl/rest/v2/reifstoreb2cstore/products/search?query=%3Arelevance%3AallCategories%3A{url_extension}&pageSize=12&currentPage={page}"
                print(products_url)
                product_containers = json.loads(session.get(products_url).text)[
                    "products"
                ]

                if not product_containers:
                    break

                for container in product_containers:
                    product_urls.append(f"https://www.aufbau.cl/p/{container['code']}")

            page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        code = url.split("/p/")[-1].replace("--", "/")
        session = session_with_proxy(extra_args)
        response = session.get(
            "https://api-prd.ynk.cl/rest/v2/reifstoreb2cstore/products/"
            "reifstore-encoding?productCode={}".format(code)
        )

        if response.status_code == 400:
            # Their own version of a 404 error
            return []

        product_info = json.loads(response.text)

        base_name = product_info["name"]
        description = html_to_markdown(product_info["description"])
        picture_urls = []

        for i in product_info["images"]:
            if i["format"] == "product":
                picture_urls.append(
                    "https://api.cxl8rgz-articulos1-p1-public"
                    ".model-t.cc.commerce.ondemand.com" + i["url"]
                )

        products = []

        if "baseOptions" in product_info and len(product_info["baseOptions"]) > 0:
            for variant in product_info["baseOptions"][0]["options"]:
                code = variant["code"]
                variant_url = "https://www.aufbau.cl" + variant["url"].replace(
                    "%2F", "--"
                )
                price = Decimal(variant["priceData"]["value"])
                stock = variant["stock"]["stockLevel"]

                variation_name = base_name + " -"

                for v in variant["variantOptionQualifiers"]:
                    variation_name += " " + v["value"]

                p = Product(
                    variation_name,
                    cls.__name__,
                    category,
                    variant_url,
                    url,
                    code,
                    stock,
                    price,
                    price,
                    "CLP",
                    sku=code,
                    part_number=code,
                    picture_urls=picture_urls,
                    description=description,
                )

                products.append(p)
        else:
            code = product_info["code"]
            price = Decimal(remove_words(product_info["price"]["formattedValue"]))
            stock_json = product_info["stock"]

            if "stockLevel" in stock_json:
                stock = stock_json["stockLevel"]
            else:
                if stock_json["stockLevelStatus"] == "inStock":
                    stock = -1
                else:
                    stock = 0

            p = Product(
                base_name,
                cls.__name__,
                category,
                url,
                url,
                code,
                stock,
                price,
                price,
                "CLP",
                sku=code,
                part_number=code,
                picture_urls=picture_urls,
                description=description,
            )

            products.append(p)

        return products
