import json
from decimal import Decimal

from bs4 import BeautifulSoup

from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import session_with_proxy, html_to_markdown
from storescraper.categories import (
    TELEVISION,
)


class Omnisport(StoreWithUrlExtensions):
    url_extensions = [["lg", TELEVISION]]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args=None):
        # KEEPS ONLY LG PRODUCTS

        session = session_with_proxy(extra_args)
        product_urls = []
        page = 1

        while True:
            if page >= 20:
                raise Exception("Page overflow")

            url = f"https://www.omnisport.com/marcas/{url_extension}?page={page}"
            print(url)

            res = session.get(url, verify=False)

            if res.url != url:
                break

            soup = BeautifulSoup(res.text, "lxml")
            containers = soup.findAll("div", "lg:w-1/3")

            if not containers:
                break

            for container in containers:
                if "lg" in container.find("p", "text-black").text.lower():
                    product_url = container.find("a", "link-basic")["href"]
                    if product_url not in product_urls:
                        product_urls.append(product_url)

            page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        response = session.get(url, verify=False)

        soup = BeautifulSoup(response.text, "lxml")
        sku = soup.find("p", "text-gray-700").contents[1].split("|")[0].strip()
        name = soup.find("h1").text.strip()
        price = Decimal(soup.find("p", "text-2xl").text.replace("$", ""))

        pictures_tag = soup.find("product-images-gallery")

        if pictures_tag:
            picture_urls = [x["full_url"] for x in json.loads(pictures_tag[":images"])]
        else:
            picture_urls = [soup.find("div", "md:w-2/5").find("img")["src"]]

        description = html_to_markdown(
            str(soup.find("div", {"id": "product-description"}).parent)
        )

        p = Product(
            name,
            cls.__name__,
            category,
            url,
            url,
            sku,
            -1,
            price,
            price,
            "USD",
            sku=sku,
            picture_urls=picture_urls,
            description=description,
        )

        return [p]
