from decimal import Decimal


from storescraper.categories import (
    SOLID_STATE_DRIVE,
    HEADPHONES,
    MOTHERBOARD,
    PROCESSOR,
    VIDEO_CARD,
    POWER_SUPPLY,
    CPU_COOLER,
    RAM,
)
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import session_with_proxy, html_to_markdown


class Campcom(StoreWithUrlExtensions):
    url_extensions = [
        ("PROCESADORES", PROCESSOR),
        ("PLACAS MADRE", MOTHERBOARD),
        ("TARJETAS DE VIDEO", VIDEO_CARD),
        ("REFRIGERACIÓN", CPU_COOLER),
        ("FUENTES DE PODER", POWER_SUPPLY),
        ("OTROS", HEADPHONES),
        ("RAM", RAM),
        ("SSD", SOLID_STATE_DRIVE),
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args=None):
        product_urls = []
        for entry in extra_args["products"]:
            if entry["prd_categoria"] != url_extension or entry["prd_url"] is None:
                continue

            product_urls.append(entry["prd_url"])

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)

        for entry in extra_args["products"]:
            if entry["prd_url"] == url:
                matching_entry = entry
                break
        else:
            raise Exception("No matching product found")

        session = session_with_proxy(extra_args)
        endpoint = f"https://campcom.cl/api/v2/products/{matching_entry['prd_id']}"
        product_data = session.get(endpoint).json()
        name = product_data["prd_title"].strip()
        key = str(product_data["prd_id"])
        stock = product_data["prd_quantity"]
        offer_price = Decimal(product_data["prd_price"])
        normal_price = Decimal(matching_entry["prd_price_tarjeta"]).quantize(0)
        sku = product_data["prd_sku"]
        picture_urls = [
            f"https://campcom.cl/api/files/productos/{product_data['prd_image'].replace(' ', '%20')}"
        ]
        description = html_to_markdown(product_data["prd_description"])

        p = Product(
            name,
            cls.__name__,
            category,
            url,
            url,
            key,
            stock,
            normal_price,
            offer_price,
            "CLP",
            sku=sku,
            picture_urls=picture_urls,
            description=description,
        )

        return [p]

    @classmethod
    def preflight(cls, extra_args=None):
        session = session_with_proxy(extra_args)
        products_json = session.get(
            "https://campcom.cl/api/v2/products/solotodo"
        ).json()["list"]
        return {"products": products_json}
