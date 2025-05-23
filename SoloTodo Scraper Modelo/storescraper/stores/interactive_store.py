from decimal import Decimal
import json
import logging
from bs4 import BeautifulSoup
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import session_with_proxy
from storescraper.categories import ALL_IN_ONE, KEYBOARD, MONITOR, NOTEBOOK, PRINTER


class InteractiveStore(StoreWithUrlExtensions):
    url_extensions = [
        ["accesorios", KEYBOARD],
        ["all-in-one", ALL_IN_ONE],
        ["gamer", NOTEBOOK],
        ["impresion-e-imagen", PRINTER],
        ["monitores-y-proyectores", MONITOR],
        ["notebooks", NOTEBOOK],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args):
        session = session_with_proxy(extra_args)
        session.headers["User-Agent"] = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36"
        )
        product_urls = []
        page = 1

        while True:
            if page > 10:
                raise Exception("Page overflow: " + url_extension)
            url_webpage = (
                "https://interactivestore.cl/categoria-producto/{}/page/{}/".format(
                    url_extension, page
                )
            )
            print(url_webpage)

            response = session.get(url_webpage)
            soup = BeautifulSoup(response.text, "lxml")
            product_containers = soup.findAll("div", "product-small")

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
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36"
        )
        response = session.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        key = soup.find("link", {"rel": "shortlink"})["href"].split("p=")[-1]

        json_data = json.loads(
            soup.find("script", {"type": "application/ld+json"}).text
        )

        if "@graph" not in json_data:
            return []

        product_data = json_data["@graph"][1]
        name = product_data["name"]
        sku = str(product_data["sku"])
        offer = product_data["offers"][0]
        price = Decimal(
            min(
                [
                    x["price"]
                    for x in offer["priceSpecification"]
                    if x["@type"] == "UnitPriceSpecification"
                ]
            )
        )
        stock = -1 if offer["availability"] == "http://schema.org/InStock" else 0
        description = product_data["description"]
        picture_urls = [product_data["image"]]

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
            picture_urls=picture_urls,
            description=description,
            part_number=sku,
        )

        return [p]
