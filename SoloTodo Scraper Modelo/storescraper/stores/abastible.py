import re
import time
from decimal import Decimal
from bs4 import BeautifulSoup
from storescraper.categories import SPLIT_AIR_CONDITIONER
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import html_to_markdown, session_with_proxy


class Abastible(StoreWithUrlExtensions):
    url_extensions = [
        ["ac-lg-dual-inverter", SPLIT_AIR_CONDITIONER],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args=None):
        time.sleep(5)
        url = "https://servicioshogar.abastible.cl/{}.html".format(url_extension)
        return [url]

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        response = session.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        key = soup.find("input", {"name": "product"})["value"]
        price = Decimal(re.search(r'"regular_price":(\d+)', response.text).groups()[0])
        name = soup.find("div", "page-title-desktop").text.strip()
        stock = -1
        description = html_to_markdown(
            soup.find("div", "product attribute description").text
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
            description=description,
        )
        return [p]
