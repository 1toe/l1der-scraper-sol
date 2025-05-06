import json
import logging
import re
from decimal import Decimal
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import session_with_proxy, html_to_markdown
from storescraper.categories import (
    TELEVISION,
    REFRIGERATOR,
    STOVE,
    OVEN,
    WASHING_MACHINE,
    SPLIT_AIR_CONDITIONER,
    MONITOR,
    ACCESORIES,
)


class LgShopEc(StoreWithUrlExtensions):
    url_extensions = [
        ["tecnologia/tv-y-video/leds-y-smart-tv", TELEVISION],
        ["electrodomesticos/refrigeracion/refrigeradoras", REFRIGERATOR],
        ["electrodomesticos/cocinas-y-hornos/cocinas", STOVE],
        ["electrodomesticos/mini-domesticos/microondas", OVEN],
        ["electrodomesticos/lavado-y-planchado/lavadoras-y-secadoras", WASHING_MACHINE],
        ["electrodomesticos/aires-acondicionados", SPLIT_AIR_CONDITIONER],
        ["tecnologia/informatica/monitores", MONITOR],
        ["tecnologia/tv-y-video/leds-y-smart-tv/accesorios-para-tv", ACCESORIES],
        [
            "electrodomesticos/refrigeracion/refrigeradoras/accesorios-para-refrigeradora",
            ACCESORIES,
        ],
        [
            "electrodomesticos/lavado-y-planchado/lavadoras-y-secadoras/accesorios-para-lavadora-y-secadora",
            ACCESORIES,
        ],
        [
            "electrodomesticos/cocinas-y-hornos/cocinas/accesorios-para-cocina",
            ACCESORIES,
        ],
        [
            "electrodomesticos/aires-acondicionados/accesorios-para-aire-acondicionado",
            ACCESORIES,
        ],
        [
            "electrodomesticos/mini-domesticos/aspiradoras/accesorios-para-aspiradora",
            ACCESORIES,
        ],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args):
        product_urls = []
        session = session_with_proxy(extra_args)
        page = 1

        while True:
            url = f"https://www.lgshop.com.ec/{url_extension}?page={page}"
            print(url)
            response = session.get(url)
            match = re.search(r"__STATE__ = {(.+)}", response.text)
            products_container = json.loads(f"{{{match.group(1)}}}")
            products = [
                key
                for key in products_container
                if re.match(r"Product:sp-\d+-(\d+--|none)$", key)
            ]

            if not products:
                if page == 1:
                    logging.warning(f"Empty section: {url}")
                break

            for product in products:
                product_url = products_container[product]["link"]
                product_urls.append(f"https://www.lgshop.com.ec{product_url}")

            page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        response = session.get(url)
        product_match = re.search(r"__STATE__ = {(.+)}", response.text)
        product_data = json.loads(f"{{{product_match.groups()[0]}}}")
        base_json_key = list(product_data.keys())[0]
        product_specs = product_data[base_json_key]
        description = html_to_markdown(product_specs.get("description", None))
        products = []
        item_idx = 0

        while True:
            item_key = f"{base_json_key}.items.{item_idx}"
            item_idx += 1

            if item_key not in product_data:
                break

            key = product_data[item_key]["itemId"]
            name = product_data[item_key]["nameComplete"]
            sku = product_data[item_key]["ean"]
            seller_entry_key = f"${item_key}.sellers.0.commertialOffer"
            seller_entry = product_data[seller_entry_key]
            price = Decimal(str(seller_entry["Price"]))

            if price == 0:
                continue

            stock = seller_entry["AvailableQuantity"]
            picture_ids = [img["id"] for img in product_data[item_key]["images"]]
            picture_urls = []

            for picture_id in picture_ids:
                picture_node = product_data[picture_id]
                picture_urls.append(
                    picture_node["imageUrl"].split("?")[0].replace(" ", "%20")
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
                "USD",
                sku=sku,
                part_number=sku,
                picture_urls=picture_urls,
                description=description,
            )
            products.append(p)

        return products
