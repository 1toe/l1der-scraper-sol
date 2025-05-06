import re
from bs4 import BeautifulSoup
from decimal import Decimal
import json
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import session_with_proxy, html_to_markdown
from storescraper.categories import (
    VACUUM_CLEANER,
    ACCESORIES,
    COOKING_ROBOT,
    AIR_FRYER,
    HAIR_CARE,
)


class Osoji(StoreWithUrlExtensions):
    url_extensions = [
        ["como-elegir-mi-aspiradora-robot/", VACUUM_CLEANER],
        ["como-elegir-mi-aspiradora-inalambrica/", VACUUM_CLEANER],
        ["shop/escobilla-electrica-b100/", ACCESORIES],
        ["como-elegir-el-mejor-robot-limpia-vidrios", ACCESORIES],
        ["shop/mopa-electrica-m400/", ACCESORIES],
        ["robots-cocina-osojimix/", COOKING_ROBOT],
        ["shop/freidora-de-aire-y-horno-de-pizza-osoji-12-lts-air-fryer/", AIR_FRYER],
        ["shop/irrigador-bucal-osoji-f100/", ACCESORIES],
        ["shop/cepillo-electrico-t100/", ACCESORIES],
        ["todos-los-robots/accesorios/", ACCESORIES],
        ["secadores-de-pelo/", HAIR_CARE],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args):
        product_urls = []
        url = f"https://osoji.cl/{url_extension}"

        if "shop" in url_extension:
            product_urls.append(url)

            return product_urls

        session = session_with_proxy(extra_args)
        print(url)
        response = session.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        product_buttons = soup.find_all(
            "span", "elementor-button-text", string="Ver más"
        )

        if product_buttons:
            for button in product_buttons:
                product_urls.append(button.find_parent("a")["href"])
        else:
            page = 1

            while True:
                if page > 1:
                    url = f"https://osoji.cl/{url_extension}page/{page}/"
                    print(url)
                    response = session.get(url)

                    if response.status_code == 404:
                        break

                    soup = BeautifulSoup(response.text, "lxml")

                for product in soup.find_all("li", "product"):
                    product_urls.append(product.find("a")["href"])

                page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        soup = BeautifulSoup(session.get(url).text, "lxml")
        product_data_tag = soup.find("input", {"name": "gtm4wp_product_data"})

        if product_data_tag:
            product_data = json.loads(product_data_tag["value"])
        else:
            product_data_text = soup.find(
                "script", {"id": "gtm4wp-additional-datalayer-pushes-js-after"}
            ).text
            product_data = json.loads(
                re.search(r"dataLayer.push\((\{.*\})\);", product_data_text).group(1)
            )["ecommerce"]["items"][0]

        name = product_data["item_name"]
        key = str(product_data["item_id"])
        stock = product_data["stocklevel"]
        price = Decimal(product_data["price"])
        sku = product_data["sku"]
        description_tag = soup.find(
            "div", "elementor-widget-woocommerce-product-content"
        ) or soup.find("div", "woocommerce-product-details__short-description")
        description = (
            html_to_markdown(description_tag.text) if description_tag else None
        )
        picture_urls = [
            img["src"] for img in soup.find("div", "wpgs-image").find_all("img")
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
