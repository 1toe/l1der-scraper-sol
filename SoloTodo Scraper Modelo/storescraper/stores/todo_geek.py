from decimal import Decimal
import json
import logging
from bs4 import BeautifulSoup
from storescraper.categories import VIDEO_CARD, VIDEO_GAME_CONSOLE, CELL, NOTEBOOK
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import html_to_markdown, remove_words, session_with_proxy


class TodoGeek(StoreWithUrlExtensions):
    url_extensions = [
        ["celulares", CELL],
        ["tarjetas-graficas", VIDEO_CARD],
        ["consolas", VIDEO_GAME_CONSOLE],
        ["notebooks", NOTEBOOK],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args):
        session = session_with_proxy(extra_args)
        product_urls = []
        page = 1
        while True:
            if page > 10:
                raise Exception("Page overflow: " + url_extension)

            url_webpage = (
                f"https://todogeek.cl/collections/{url_extension}/page/{page}/"
            )
            print(url_webpage)

            res = session.get(url_webpage)
            soup = BeautifulSoup(res.text, "lxml")
            product_containers = soup.findAll("div", "product-content")

            if not product_containers:
                if page == 1:
                    logging.warning(f"Empty category: {url_extension}")
                break

            for container in product_containers:
                product_urls.append(container.find("a")["href"])
            page += 1
        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        response = session.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        page_data = json.loads(
            soup.findAll("script", {"type": "application/ld+json"})[0].text
        )["@graph"]

        product_variations = soup.find("form", "variations_form")

        if product_variations:
            products = []

            for entry in page_data:
                if entry["@type"] == "ProductGroup":
                    product_entries = entry["hasVariant"]
                    break
            else:
                return []

            variations_data = json.loads(product_variations["data-product_variations"])
            assert len(variations_data) == len(product_entries)

            # We have to assume that the product entries and the variation data is in the same order,
            # there is no common key to match them consistently
            for product_entry, variation_data in zip(product_entries, variations_data):
                key = str(variation_data["variation_id"])
                name = f"{product_entry['name']} ({', '.join(variation_data['attributes'].values())})"
                sku = variation_data["sku"]

                if sku == "":
                    sku = None

                description = html_to_markdown(
                    soup.find("div", {"id": "tab-description"}).text
                )
                offer_price = Decimal(variation_data["display_price"])
                normal_price = (offer_price * Decimal("1.06")).quantize(0)
                stock = -1 if variation_data["is_in_stock"] else 0
                picture_urls = [variation_data["image"]["url"]]

                condition_tag = soup.find("p", "product-condition")

                if (
                    condition_tag
                    and "producto: nuevo" not in condition_tag.text.lower()
                ):
                    condition = "https://schema.org/RefurbishedCondition"
                else:
                    condition = "https://schema.org/NewCondition"

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
                    condition=condition,
                    sku=sku,
                    part_number=sku,
                    picture_urls=picture_urls,
                    description=description,
                )

                products.append(p)

            return products
        else:
            for entry in page_data:
                if entry["@type"] == "Product":
                    product_data = entry
                    break
            else:
                return []

            name = product_data["name"]
            sku = str(product_data["sku"]) if "sku" in product_data else None
            offer = product_data["offers"]
            stock = -1 if offer["availability"] == "https://schema.org/InStock" else 0

            offer_price = Decimal(
                remove_words(soup.find("p", "price-transferencia").find("bdi").text)
            )
            normal_price = Decimal(
                remove_words(soup.find("p", "price-debito-credito").find("bdi").text)
            )
            description = html_to_markdown(product_data.get("description", ""))
            key = soup.find("link", {"rel": "shortlink"})["href"].split("?p=")[-1]
            picture_urls = [
                a["href"]
                for a in soup.find(
                    "div", "woocommerce-product-gallery__wrapper"
                ).findAll("a")
            ]

            categories = [
                category.text.lower()
                for category in soup.find("span", "posted_in").findAll("a")
            ]

            if "seminuevos" in categories or "seminuevo" in name:
                condition = "https://schema.org/RefurbishedCondition"
            elif "open box" in categories or "open box" in name:
                condition = "https://schema.org/OpenBoxCondition"
            else:
                condition = "https://schema.org/NewCondition"

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
                description=description,
                condition=condition,
            )

            return [p]
