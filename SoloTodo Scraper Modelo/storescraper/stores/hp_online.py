import logging

from bs4 import BeautifulSoup
from decimal import Decimal

from storescraper.categories import (
    MONITOR,
    NOTEBOOK,
    PRINTER,
    ALL_IN_ONE,
    MOUSE,
    HEADPHONES,
    PRINTER_SUPPLY,
)
from storescraper.product import Product
from storescraper.store import Store
from storescraper.utils import (
    session_with_proxy,
    html_to_markdown,
    magento_picture_urls,
)


class HpOnline(Store):
    @classmethod
    def categories(cls):
        return [
            NOTEBOOK,
            PRINTER,
            MONITOR,
            ALL_IN_ONE,
            MOUSE,
            HEADPHONES,
            PRINTER_SUPPLY,
        ]

    @classmethod
    def discover_urls_for_category(cls, category, extra_args=None):
        category_paths = [
            ["notebooks", NOTEBOOK],
            ["impresoras", PRINTER],
            ["monitores", MONITOR],
            ["desktops", ALL_IN_ONE],
            ["accesorios/mouse-teclados", MOUSE],
            ["accesorios/bocinas-audio", HEADPHONES],
            ["tinta-toner", PRINTER_SUPPLY],
        ]
        session = session_with_proxy(extra_args)
        session.headers["Content-Type"] = (
            "application/x-www-form-urlencoded; charset=UTF-8"
        )
        session.headers["X-Requested-With"] = "XMLHttpRequest"
        product_urls = []

        for category_path, local_category in category_paths:
            if local_category != category:
                continue

            page = 1

            while True:
                if page > 40:
                    break
                    # raise Exception("page overflow: " + category_path)
                category_url = f"https://www.hp.com/cl-es/shop/{category_path}.html?product_list_limit=36&p={page}"
                print(category_url)
                response = session.post(category_url, "filter_ajax=true")
                json_response = response.json()
                soup = BeautifulSoup(json_response["productlist"], "lxml")
                product_cells = soup.findAll("li", "product")

                if not product_cells:
                    if page == 1:
                        logging.warning("Empty category: " + category_url)
                    break

                new_products_found = False

                for cell in product_cells:
                    product_url = cell.find("a", "product-item-link")["href"]

                    if product_url not in product_urls:
                        new_products_found = True
                        product_urls.append(product_url)

                if not new_products_found or not product_cells:
                    break

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

        if soup.find("ol", "products"):
            return []

        name_tag = soup.find("span", {"itemprop": "name"})

        if not name_tag:
            return []

        name = name_tag.text.strip()
        sku = soup.find("div", {"itemprop": "sku"}).text.strip()
        stock = -1

        price_container = soup.find("span", {"data-price-type": "finalPrice"})

        if not price_container or not price_container.find("span", "price"):
            return []

        price = price_container.find("span", "price").text.strip()
        price = Decimal(price.replace("$", "").replace(".", ""))

        description = html_to_markdown(
            str(soup.find("div", "product info detailed").find("div", "overview"))
        )

        picture_urls = magento_picture_urls(soup)

        p = Product(
            name,
            cls.__name__,
            category,
            url,
            url,
            sku,
            stock,
            price,
            price,
            "CLP",
            sku=sku,
            part_number=sku,
            description=description,
            picture_urls=picture_urls,
        )

        return [p]
