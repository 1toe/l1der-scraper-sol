import logging
import json
import re

from decimal import Decimal
from bs4 import BeautifulSoup

from storescraper.categories import (
    MONITOR,
    RAM,
    UPS,
    STORAGE_DRIVE,
)
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import html_to_markdown, remove_words, session_with_proxy


class VideoVision(StoreWithUrlExtensions):
    url_extensions = [
        ["monitores", MONITOR],
        ["ups", UPS],
        ["memorias", RAM],
        ["discos-duros", STORAGE_DRIVE],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args=None):
        session = session_with_proxy(extra_args)
        product_urls = []
        page = 1

        while True:
            if page > 10:
                raise Exception("page overflow: " + url_extension)

            url_webpage = (
                f"https://videovision.cl/collections/{url_extension}?page={page}"
            )
            print(url_webpage)

            response = session.get(url_webpage)
            soup = BeautifulSoup(response.text, "lxml")
            product_links = soup.find("div", "collection").findAll("a", "card-link")

            if not product_links:
                if page == 1:
                    logging.warning("Empty category: " + url_extension)

                break

            for link in product_links:
                product_urls.append(f"https://videovision.cl{link['href']}")

            page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        response = session.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        product_script = soup.findAll("script", {"type": "application/ld+json"})[1].text
        product_script = re.sub(r"\s+", " ", product_script)
        product_data = json.loads(product_script)

        offer = product_data["offers"]
        name = offer["name"]
        stock = -1 if offer["availability"] == "http://schema.org/InStock" else 0
        price = Decimal(offer["price"])
        sku = offer["sku"]
        key = offer["url"].split("?variant=")[-1]
        description = html_to_markdown(
            soup.find("div", {"id": "tab-description"})
            .find("div", "tab-popup-content")
            .text
        )
        picture_containers = soup.findAll("div", "product-single__media")
        picture_urls = []

        for container in picture_containers:
            picture_urls.append(f"https:{container.find('div', 'media')['href']}")

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
        )

        return [p]
