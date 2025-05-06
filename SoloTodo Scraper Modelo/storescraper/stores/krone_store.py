from bs4 import BeautifulSoup
from decimal import Decimal
import json
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import session_with_proxy, html_to_markdown
from storescraper.categories import GAMING_CHAIR


class KroneStore(StoreWithUrlExtensions):
    url_extensions = [
        ["sillas-gamer-oficina-krone-xl", GAMING_CHAIR],
        ["krone-signature", GAMING_CHAIR],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args):
        product_urls = []
        session = session_with_proxy(extra_args)
        page = 1

        while True:
            url = f"https://kronestore.cl/collections/{url_extension}?page={page}"
            print(url)
            response = session.get(url)
            soup = BeautifulSoup(response.text, "lxml")
            products = soup.findAll("li", "grid__item")

            if not products:
                if page == 1:
                    raise Exception("Invalid section: " + url)
                break

            for product in products:
                product_url = f"https://kronestore.cl{product.find('a')['href']}"
                product_urls.append(product_url)

            page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        soup = BeautifulSoup(session.get(url).text, "lxml")
        product_data = json.loads(
            soup.find_all("script", {"type": "application/ld+json"})[1].text
        )

        name = product_data["name"]
        sku = product_data["sku"]
        offer = product_data["offers"]
        price = Decimal(offer["price"])
        key = offer["url"].split("?variant=")[-1]
        stock = -1 if offer["availability"] == "http://schema.org/InStock" else 0
        description = html_to_markdown(product_data["description"])
        picture_urls = [
            f"https:{img['src'].split('?v=')[0]}"
            for img in soup.find_all("img", "image-magnify-lightbox")
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
            "CLP",
            sku=sku,
            description=description,
            picture_urls=picture_urls,
        )

        return [p]
