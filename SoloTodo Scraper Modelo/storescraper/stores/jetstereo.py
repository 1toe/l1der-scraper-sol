import json
import logging
import re
import urllib
from decimal import Decimal

from bs4 import BeautifulSoup

from storescraper.product import Product
from storescraper.store import Store
from storescraper.utils import session_with_proxy
from storescraper.categories import TELEVISION


class Jetstereo(Store):
    preferred_discover_urls_concurrency = 1
    preferred_products_for_url_concurrency = 1
    base_url = "https://www.jetstereo.com"

    @classmethod
    def categories(cls):
        return [TELEVISION]

    @classmethod
    def discover_urls_for_category(cls, category, extra_args=None):
        session = session_with_proxy(extra_args)
        product_urls = []
        page = 1
        while True:
            if page > 20:
                raise Exception("Page overflow")
            url = (
                "https://api.jetstereo.com/manufacturers/2/products?"
                "per-page=20&page={}".format(page)
            )
            print(url)
            response = session.get(url)
            product_containers = json.loads(response.text)
            if page > product_containers["_meta"]["pageCount"]:
                break
            product_containers = product_containers["content"]

            if not product_containers:
                if page == 1:
                    logging.warning("Empty category: " + url)
                break

            for container in product_containers:
                product_url = container["url"]
                product_urls.append(product_url)
            page += 1
        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        response = session.get(url, verify=False)
        soup = BeautifulSoup(response.text, "lxml")
        scripts = soup.findAll("script")

        for script in scripts:
            if "saleStatus" in script.text:
                product_script = script.text
                break
        else:
            raise Exception("No product script tag found")

        for entry in re.findall(r"({.*})", product_script):
            if "saleStatus" in entry:
                product_entry = entry
                break
        else:
            raise Exception("No product entry tag found")

        product_json = json.loads(
            product_entry.replace('\\\\"', "")
            .replace("\\", "")
            .split(
                '],["$","script",null,{"type":"application/ld+json","dangerouslySetInnerHTML"'
            )[0]
        )["product"]

        name = product_json["name"]
        sku = str(product_json["id"])
        part_number = product_json["sku"]

        if product_json["saleStatus"] == "AVAILABLE":
            stock = -1
        else:
            stock = 0

        price = Decimal(product_json["price"]["sale"]).quantize(Decimal(".01"))
        picture_urls = [
            urllib.parse.quote(picture_url, safe="://")
            for picture_url in product_json["allImages"]["full"]
        ]
        description = product_json["description"]["description"]

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
            sku=sku,
            picture_urls=picture_urls,
            part_number=part_number,
            description=description,
        )

        return [p]
