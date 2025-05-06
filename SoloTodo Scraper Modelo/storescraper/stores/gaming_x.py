from decimal import Decimal
import logging
import json
from storescraper.product import Product
from bs4 import BeautifulSoup
from storescraper.categories import NOTEBOOK, MONITOR, CPU_COOLER, VIDEO_CARD
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import cf_session_with_proxy, html_to_markdown, remove_words


class GamingX(StoreWithUrlExtensions):
    @classmethod
    def categories(cls):
        return [NOTEBOOK, MONITOR, CPU_COOLER, VIDEO_CARD]

    @classmethod
    def discover_urls_for_category(cls, category, extra_args=None):
        url_extensions = [
            ("notebooks", NOTEBOOK),
            ("monitores", MONITOR),
            ("refrigeracion", CPU_COOLER),
            ("tarjetas-de-video", VIDEO_CARD),
        ]

        session = cf_session_with_proxy(extra_args)
        product_urls = []

        for url_extension, local_category in url_extensions:
            if local_category != category:
                continue

            page = 1

            while True:
                if page > 10:
                    raise Exception(f"Page overflow: {url_extension}")

                url_webpage = f"https://www.gamingx.cl/{url_extension}/page/{page}"
                print(url_webpage)
                data = session.get(url_webpage)
                soup = BeautifulSoup(data.text, "lxml")
                product_containers = soup.findAll("div", "product-item")

                if not product_containers:
                    if page == 1:
                        logging.warning(f"Empty category: {url_extension}")
                    break

                for container in product_containers:
                    product_url = container.find("a")["href"]
                    product_urls.append(product_url)
                page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = cf_session_with_proxy(extra_args)
        soup = BeautifulSoup(session.get(url).text, "lxml")
        products = []
        variations = soup.find("div", {"id": "single-product"})
        name = soup.find("h1", "js-product-name").text.strip()

        for variation in json.loads(variations.get("data-variants")):
            key = str(variation["product_id"])
            stock = variation["stock"]
            price = Decimal(remove_words(variation["price_short"]))
            offer_price = Decimal(
                remove_words(variation["price_with_payment_discount_short"])
            )
            sku = variation["sku"]
            description = html_to_markdown(
                soup.find("div", {"data-store": f"product-description-{key}"}).text
            )
            picture_urls = [
                slide.find("a")["href"]
                for slide in soup.findAll(
                    "div", "js-product-slide swiper-slide slider-slide"
                )
            ]

            for i, picture_url in enumerate(picture_urls):
                if "https:" not in picture_url:
                    picture_urls[i] = f"https:{picture_url}"

            p = Product(
                name,
                cls.__name__,
                category,
                url,
                url,
                key,
                stock,
                price,
                offer_price,
                "CLP",
                sku=sku,
                description=description,
                picture_urls=picture_urls,
            )

            products.append(p)

        return products
