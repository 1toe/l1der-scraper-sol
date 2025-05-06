from bs4 import BeautifulSoup
from decimal import Decimal
import json
from storescraper.categories import ACCESORIES, MONITOR, PRINTER, PRINTER_SUPPLY
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import html_to_markdown, session_with_proxy


class LaserChile(StoreWithUrlExtensions):
    url_extensions = [
        ("impresoras", PRINTER),
        ("mas-categorias", ACCESORIES),
        ("monitores", MONITOR),
        ("tintas", PRINTER_SUPPLY),
        ("toner", PRINTER_SUPPLY),
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args):
        product_urls = []
        session = session_with_proxy(extra_args)
        page = 1

        while True:
            url = f"https://laserchile.com/categoria-producto/{url_extension}/page/{page}/"
            print(url)
            response = session.get(url)

            if response.status_code == 404:
                if page == 1:
                    raise Exception(f"Empty section: {url}")
                break

            soup = BeautifulSoup(response.text, "lxml")
            products_container = soup.find("ul", "products")

            for product in products_container.find_all("li", "product-type-simple"):
                product_url = product.find("a", "woocommerce-LoopProduct-link")["href"]
                product_urls.append(product_url)

            page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        soup = BeautifulSoup(session.get(url).text, "lxml")
        product_data_tag = soup.find("input", {"name": "gtm4wp_product_data"})

        if not product_data_tag:
            return []

        product_data = json.loads(product_data_tag["value"])
        name = product_data["item_name"]

        if "alternativo" in name.lower():
            return []

        key = str(product_data["item_id"])
        stock = -1 if soup.find("button", {"name": "add-to-cart"}) else 0
        price = Decimal(product_data["price"]).quantize(0)
        sku = str(product_data["sku"])
        description_tag = (
            soup.find("div", "elementor-widget-woocommerce-product-content")
            or soup.find("div", "woocommerce-product-details__short-description")
            or soup.find("div", {"id": "tab-description"})
        )
        description = (
            html_to_markdown(description_tag.text) if description_tag else None
        )
        picture_urls = [
            img.find("a")["href"]
            for img in soup.find_all("div", "woocommerce-product-gallery__image")
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
