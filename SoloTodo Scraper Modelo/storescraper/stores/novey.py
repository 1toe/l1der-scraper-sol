from decimal import Decimal
import json
import re
from bs4 import BeautifulSoup
from storescraper.categories import TELEVISION
from storescraper.product import Product
from storescraper.store import Store
from storescraper.utils import html_to_markdown, remove_words, session_with_proxy


class Novey(Store):
    @classmethod
    def categories(cls):
        return [TELEVISION]

    @classmethod
    def discover_urls_for_category(cls, category, extra_args=None):
        # Only interested in LG products

        if TELEVISION != category:
            return []

        session = session_with_proxy(extra_args)
        response = session.get(
            "https://www.novey.com.pa/productos-tv-audio-electronica-y-celulares/televisores-smart-tv"
        )
        soup = BeautifulSoup(response.text, "lxml")

        for script in soup.find_all("script"):
            if script.string and script.string.startswith("window.algoliaConfig"):
                algolia_json_content = re.search(
                    r"window\.algoliaConfig\s*=\s*(\{.*\});", script.string
                ).group(1)
                algolia_data = json.loads(algolia_json_content)
                algolia_application_id = algolia_data["applicationId"]
                algolia_api_key = algolia_data["apiKey"]
                break

        product_urls = []
        payload = {
            "requests": [
                {
                    "indexName": "magento2_prod_new1_novey_panama_products",
                    "params": "hitsPerPage=300&page=0&query=lg",
                }
            ]
        }
        session.headers = {
            "x-algolia-api-key": algolia_api_key,
            "x-algolia-application-id": algolia_application_id,
        }
        page = 0

        while True:
            url = "https://zczrbtyd8i-dsn.algolia.net/1/indexes/*/queries"
            payload["requests"][0]["params"] = f"hitsPerPage=300&page={page}&query=lg"
            response = json.loads(session.post(url, json=payload).text)
            products = response["results"][0]["hits"]

            if not products:
                break

            for product in products:
                product_urls.append(product["url"])

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
        name = soup.find("h1", "page-title").text.strip()

        if name == "Default Novey":
            return []

        key = str(soup.find("input", {"name": "product"})["value"])
        sku = soup.find("div", {"itemprop": "sku"}).text.strip()
        price_container = soup.find("div", "product-info-price")
        price = Decimal(
            remove_words(price_container.find("span", "price").text, ["$", ","])
        )
        description = None
        description_container = soup.find("div", {"id": "description"})

        if description_container:
            description = html_to_markdown(
                description_container.find("div", "product-detailed-info").text
            )

        stock_container = soup.find("div", "stock available")
        stock = (
            -1
            if stock_container and stock_container.text.strip() == "Disponible"
            else 0
        )
        magento_scripts = soup.findAll("script", {"type": "text/x-magento-init"})
        pictures_data = None

        for script in magento_scripts:
            data = json.loads(script.text)

            if "[data-gallery-role=gallery-placeholder]" in data:
                pictures_data = data["[data-gallery-role=gallery-placeholder]"][
                    "mage/gallery/gallery"
                ]["data"]
                break

        picture_urls = [img["img"].split("?")[0] for img in pictures_data]

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
            "USD",
            sku=sku,
            picture_urls=picture_urls,
            description=description,
        )

        return [p]
