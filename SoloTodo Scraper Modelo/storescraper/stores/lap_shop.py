import json
from decimal import Decimal

from bs4 import BeautifulSoup

from storescraper.categories import ACCESORIES, MONITOR
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import html_to_markdown, session_with_proxy, remove_words


class LapShop(StoreWithUrlExtensions):
    url_extensions = [
        ["monitores-business", MONITOR],
        ["monitores-gamer", MONITOR],
        ["outlet", MONITOR],
        ["cables", ACCESORIES],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args=None):
        session = session_with_proxy(extra_args)
        product_urls = []
        page = 1
        while True:
            if page > 10:
                raise Exception("page overflow")

            url_webpage = f"https://lapshop.cl/collections/{url_extension}?page={page}"
            print(url_webpage)
            res = session.get(url_webpage)
            soup = BeautifulSoup(res.text, "lxml")
            product_containers = soup.findAll("li", "productgrid--item")

            if not product_containers:
                break

            for container in product_containers:
                product_url = container.find("a")["href"]
                product_urls.append(f"https://www.lapshop.cl{product_url}")
            page += 1
        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        response = session.get(url)

        if response.status_code == 404:
            return []

        soup = BeautifulSoup(response.text, "lxml")
        product_data = json.loads(
            soup.find_all("script", {"type": "application/ld+json"})[1].text
        )
        key = soup.find("script", {"id": "quote_product_current_id"}).text.strip()
        name = product_data["name"]
        sku = product_data["sku"]
        offer = product_data["offers"]
        stock = -1 if offer["availability"] == "http://schema.org/InStock" else 0
        normal_price = Decimal(offer["price"])
        offer_price = Decimal(remove_words(soup.find("span", "money").text))

        if offer_price > normal_price:
            offer_price = normal_price

        if "SEGUNDA" in name.upper():
            condition = "https://schema.org/RefurbishedCondition"
        else:
            condition = "https://schema.org/NewCondition"

        picture_urls = [
            f"https://{x['data-zoom'][2:]}"
            for x in soup.find_all("figure", "product-gallery--image")
        ]
        description = html_to_markdown(soup.find("section", "custom-liquid").text)

        p = Product(
            name,
            cls.__name__,
            category,
            url,
            url,
            key,
            stock,
            normal_price,
            offer_price,
            "CLP",
            sku=sku,
            picture_urls=picture_urls,
            condition=condition,
            description=description,
        )
        return [p]
