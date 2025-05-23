from decimal import Decimal
import json
import logging
import re

from bs4 import BeautifulSoup

from storescraper.categories import (
    NOTEBOOK,
    MONITOR,
    STORAGE_DRIVE,
    SOLID_STATE_DRIVE,
    RAM,
    VIDEO_CARD,
    UPS,
    ALL_IN_ONE,
)
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import session_with_proxy, html_to_markdown, remove_words


class GestionYEquipos(StoreWithUrlExtensions):
    url_extensions = [
        ["computadoras-portatiles", NOTEBOOK],
        ["monitores", MONITOR],
        ["disco-duro-hdd", STORAGE_DRIVE],
        ["disco-solido", SOLID_STATE_DRIVE],
        ["pc-de-escritorio-dimm", RAM],
        ["portatiles-sodimm", RAM],
        ["tarjetas-de-video", VIDEO_CARD],
        ["unidad-de-respaldo-de-energia", UPS],
        ["pc-de-escritorio", ALL_IN_ONE],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args):
        session = session_with_proxy(extra_args)
        product_urls = []
        page = 1
        while True:
            if page > 10:
                raise Exception("page overflow: " + url_extension)
            url_webpage = "https://gestionyequipos.cl/collections/{}?page={}".format(
                url_extension, page
            )
            print(url_webpage)
            res = session.get(url_webpage)
            soup = BeautifulSoup(res.text, "lxml")
            product_containers = soup.findAll("li", "js-pagination-result")
            if not product_containers:
                if page == 1:
                    logging.warning("Empty category: " + url_extension)
                break
            for container in product_containers:
                product_url = "https://gestionyequipos.cl" + container.find("a")["href"]
                product_urls.append(product_url)
            page += 1
        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        response = session.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        description = html_to_markdown(str(soup.find("div", "product-details__block")))
        condition_text = soup.find("span", "product-label").text.strip().upper()

        condition_dict = {
            "REACONDICIONADO": "https://schema.org/RefurbishedCondition",
            "NUEVO": "https://schema.org/NewCondition",
            "NUEVO CAJA ABIERTA": "https://schema.org/OpenBoxCondition",
        }
        condition = condition_dict[condition_text]

        products = []
        variants_tags = soup.findAll("script", {"type": "application/json"})

        if len(variants_tags) > 4:
            variants_json = json.loads(variants_tags[4].text)
            picture_urls = ["https:" + x for x in variants_json["product"]["images"]]

            for variant in variants_json["product"]["variants"]:
                key = str(variant["id"])
                variant_url = url + "?variant={}".format(key)
                sku = variant["sku"]
                stock = -1 if variant["available"] else 0
                price = Decimal(variant["price"] / 100)

                p = Product(
                    sku,
                    cls.__name__,
                    category,
                    variant_url,
                    url,
                    key,
                    stock,
                    price,
                    price,
                    "CLP",
                    sku=sku,
                    part_number=sku,
                    picture_urls=picture_urls,
                    description=description,
                    condition=condition,
                )
                products.append(p)

            return products
        else:
            json_container = soup.findAll("script", {"type": "application/ld+json"})[-1]
            json_data = json.loads(json_container.text)
            picture_urls = [
                "https:" + x["href"] for x in soup.findAll("a", "media--cover")
            ]

        if "hasVariant" in json_data:
            for variant in json_data["hasVariant"]:
                name = variant["name"]
                key = re.search(r"variant=(\d+)", variant["@id"]).group(1)
                sku = variant["sku"]
                offer = variant["offers"]
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
                    sku=sku,
                    part_number=sku,
                    picture_urls=picture_urls,
                    description=description,
                    condition=condition,
                )
                products.append(p)
        else:
            key = soup.find("input", {"name": "id"})["value"]
            name = json_data["name"].strip()
            offer = json_data["offers"]
            price = Decimal(offer["price"])
            stock = -1 if offer["availability"] == "http://schema.org/InStock" else 0
            container = soup.find("div", "product-info")
            sku = container.find("span", "product-sku__value").text.strip()

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
                part_number=sku,
                picture_urls=picture_urls,
                description=description,
                condition=condition,
            )
            products.append(p)

        return products
