from bs4 import BeautifulSoup

from storescraper.categories import CELL, WEARABLE
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import session_with_proxy


class TiendaClaro(StoreWithUrlExtensions):
    url_extensions = [
        (
            "categoryId=3074457345616686668&facet_2=ads_f12001_ntk_cs%253A%2522itemShow%2522&facet_1=ads_f11503_ntk_cs%253A%2522Liberados%2522",
            CELL,
        ),
        ("categoryId=3074457345616688192", WEARABLE),
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args=None):
        product_urls = []
        session = session_with_proxy(extra_args)
        session.headers["User-Agent"] = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )
        session.headers["Accept-Language"] = "en"
        offset = 0

        while True:
            category_url = "https://tienda.clarochile.cl/CategoryDisplay?{}&storeId=10151&beginIndex={}".format(
                url_extension, offset
            )
            print(category_url)
            soup = BeautifulSoup(session.get(category_url).text, "lxml")

            containers = soup.findAll("div", "product_info")

            if not containers:
                if offset == 0:
                    raise Exception("Empty list")

                break

            for container in containers:
                product_url = container.find_all("a")[1]["href"]
                product_urls.append(product_url)

            offset += 12

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        from .claro import Claro

        extra_args = extra_args or {}
        extra_args["combination_types"] = ["PRE", ""]

        products = Claro.products_for_url(url, category, extra_args)

        for product in products:
            product.cell_monthly_payment = None

        return products
