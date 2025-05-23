import json
import logging
from decimal import Decimal

from bs4 import BeautifulSoup

from storescraper.categories import (
    CELL,
    COMPUTER_CASE,
    PROCESSOR,
    VIDEO_CARD,
    VIDEO_GAME_CONSOLE,
    POWER_SUPPLY,
    NOTEBOOK,
)
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import (
    get_price_from_price_specification,
    html_to_markdown,
    session_with_proxy,
)


class SmartMobile(StoreWithUrlExtensions):
    url_extensions = [
        ["smartphones", CELL],
        ["procesador", PROCESSOR],
        ["tarjeta-grafica", VIDEO_CARD],
        ["gabinete", COMPUTER_CASE],
        ["fuente-de-poder", POWER_SUPPLY],
        ["consolas", VIDEO_GAME_CONSOLE],
        ["macbook", NOTEBOOK],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args=None):
        session = session_with_proxy(extra_args)
        session.headers["User-Agent"] = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36"
        )
        product_urls = []
        page = 1

        while True:
            if page > 10:
                raise Exception("page overflow: " + url_extension)
            url_webpage = (
                "https://smartmobile.cl/categoria-producto/"
                "{}/page/{}/".format(url_extension, page)
            )
            print(url_webpage)
            data = session.get(url_webpage).text
            soup = BeautifulSoup(data, "html5lib")
            product_containers = soup.find("main", "site-main").find("ul", "products")

            if soup.find("div", "info-404") or not product_containers:
                if page == 1:
                    logging.warning("Empty category: " + url_extension)

                break

            for container in product_containers.findAll("li", "product"):
                product_url = container.find("a", "woocommerce-loop-product__link")[
                    "href"
                ]
                product_urls.append(product_url)

            page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        session.headers["User-Agent"] = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36"
        )
        response = session.get(url)
        soup = BeautifulSoup(response.text, "lxml")

        product_container = soup.find("div", "single-product-wrapper")
        name = product_container.find("h1", "product_title").text

        tags = product_container.find("span", "loop-product-categories").findAll("a")

        for tag in tags:
            if "PEDIDO" in tag.text.upper():
                force_unavailable = True
                break
        else:
            force_unavailable = False

        if "PEDIDO" in name.upper():
            force_unavailable = True

        if (
            "USAD" in name.upper()
            or "SIN CAJA" in name.upper()
            or "REACON" in name.upper()
            or "SEMINUEVO" in name.upper()
        ):
            condition = "https://schema.org/RefurbishedCondition"
        else:
            condition = "https://schema.org/NewCondition"

        description = html_to_markdown(soup.find("div", {"id": "tab-description"}).text)

        if soup.find("form", "variations_form cart"):
            products = []
            variations = json.loads(
                soup.find("form", "variations_form cart")["data-product_variations"]
            )

            for variation in variations:
                variation_attribute = list(variation["attributes"].values())
                variation_name = name + " (" + " - ".join(variation_attribute) + ")"
                sku = str(variation["variation_id"])
                offer_price = Decimal(variation["display_price"])
                normal_price = Decimal(round(variation["display_price"] * 1.04))

                if force_unavailable:
                    stock = 0
                elif variation["availability_html"] == "":
                    stock = -1
                elif (
                    BeautifulSoup(variation["availability_html"], "lxml").text.split()[
                        0
                    ]
                    == "Agotado"
                ):
                    stock = 0
                else:
                    stock_text = BeautifulSoup(
                        variation["availability_html"], "lxml"
                    ).text.strip()
                    if stock_text == "Hay existencias":
                        # A pedido
                        stock = 0
                    elif stock_text == "Sin existencias":
                        stock = 0
                    else:
                        stock = int(stock_text.split()[0])

                picture_urls = [variation["image"]["url"]]

                p = Product(
                    variation_name,
                    cls.__name__,
                    category,
                    url,
                    url,
                    sku,
                    stock,
                    normal_price,
                    offer_price,
                    "CLP",
                    sku=sku,
                    picture_urls=picture_urls,
                    condition=condition,
                    description=description,
                )

                products.append(p)

            return products
        else:
            json_data = json.loads(
                soup.find("script", {"type": "application/ld+json"}).text
            )

            if "@graph" not in json_data:
                return []

            offer_price = get_price_from_price_specification(json_data["@graph"][1])
            normal_price = round(offer_price * Decimal(1.06), 2)
            sku = soup.find("link", {"rel": "shortlink"})["href"].split("=")[-1]

            if force_unavailable:
                stock = 0
            elif not product_container.find("p", "stock"):
                stock = -1
            else:
                stock_container = product_container.find("p", "stock").text.split()
                if stock_container[0] == "Agotado":
                    stock = 0
                elif stock_container[0] == "Sin":  # Sin existencias
                    stock = 0
                elif stock_container[0] == "Hay":  # Hay existencias
                    stock = -1
                else:
                    stock = int(stock_container[0])

            picture_urls = [
                tag["src"]
                for tag in soup.find("div", "woocommerce-product-gallery").findAll(
                    "img"
                )
            ]

            p = Product(
                name,
                cls.__name__,
                category,
                url,
                url,
                sku,
                stock,
                normal_price,
                offer_price,
                "CLP",
                sku=sku,
                picture_urls=picture_urls,
                condition=condition,
                description=description,
            )

            return [p]
