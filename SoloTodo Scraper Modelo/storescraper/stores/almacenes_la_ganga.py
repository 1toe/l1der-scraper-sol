import re

from decimal import Decimal
from bs4 import BeautifulSoup

from storescraper.product import Product
from storescraper.store import Store
from storescraper.utils import html_to_markdown, session_with_proxy
from storescraper.categories import TELEVISION


class AlmacenesLaGanga(Store):
    @classmethod
    def categories(cls):
        return [
            TELEVISION,
        ]

    @classmethod
    def discover_urls_for_category(cls, category, extra_args=None):
        if category != TELEVISION:
            return []

        session = session_with_proxy(extra_args)
        product_urls = []
        page = 1

        while True:
            if page > 10:
                raise Exception("Page overflow")

            url = f"https://laganga.com/catalogsearch/result/?q=LG&p={page}"
            print(url)
            soup = BeautifulSoup(session.get(url).text, "lxml")
            products = soup.findAll("li", "item product product-item")

            if not products:
                if page == 1:
                    raise Exception("Empty store")
                break

            for product in products:
                product_urls.append(product.find("a")["href"])

            page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        response = session.get(url)
        soup = BeautifulSoup(response.text, "lxml")

        cart_form = soup.find("form", {"id": "product_addtocart_form"})
        key = cart_form.find("input", {"name": "product"})["value"]
        name = soup.find("span", {"itemprop": "name"}).text.strip()
        sku = soup.find("div", {"itemprop": "sku"}).text
        price = Decimal(soup.find("meta", {"itemprop": "price"})["content"])
        stock_tag = soup.find("div", "stock available")
        stock = -1 if stock_tag and stock_tag.text.strip().lower() == "en stock" else 0
        part_number = soup.find("td", {"data-th": "Modelo"}).text.strip()
        description = html_to_markdown(
            soup.find("div", {"itemprop": "description"}).text
        )
        slider = soup.find("div", "p-thumb-nav slick-slider")
        picture_urls = [img["src"] for img in slider.findAll("img")]

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
            part_number=part_number,
            picture_urls=picture_urls,
            description=description,
        )

        return [p]
