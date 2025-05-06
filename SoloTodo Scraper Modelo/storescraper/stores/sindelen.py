import json
import re
from decimal import Decimal
from bs4 import BeautifulSoup
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.product import Product
from storescraper.utils import session_with_proxy, remove_words, html_to_markdown
from storescraper.categories import (
    ACCESORIES,
    STOVE,
    OVEN,
    REFRIGERATOR,
    VACUUM_CLEANER,
    WASHING_MACHINE,
    WATER_HEATER,
    SPLIT_AIR_CONDITIONER,
    SPACE_HEATER,
    MIXER,
    BLENDER,
    COFFE_MAKER,
    AIR_FRYER,
    ELECTRIC_POT,
    TOASTER,
    COOKING_ROBOT,
    IRON,
    HAIR_CARE,
)


class Sindelen(StoreWithUrlExtensions):
    url_extensions = [
        ("10152/cocinas-y-encimeras", STOVE),
        ("10022/hornos-electricos", OVEN),
        ("10023/hornos-electricos", OVEN),
        ("10026/hornos-electricos", OVEN),
        ("10012/campanas", ACCESORIES),
        ("10116/Refrigeracion", REFRIGERATOR),
        ("10154/batidoras-y-picadoras", MIXER),
        ("10155/licuadoras-y-extractores", BLENDER),
        ("10156/cafeteras-y-hervidores", COFFE_MAKER),
        ("10157/freidoras-y-parrillas", AIR_FRYER),
        ("10027/ollas-electricas", ELECTRIC_POT),
        ("10158/tostadores-y-sandwicheras", TOASTER),
        ("10071/cocedor-de-huevos", ACCESORIES),
        ("10072/maquina-para-hacer-pan", ACCESORIES),
        ("10073/soup-maker", ACCESORIES),
        ("10074/robot-de-cocina", COOKING_ROBOT),
        ("10036/aspiradoras", VACUUM_CLEANER),
        ("10037/enceradoras-y-mopas", ACCESORIES),
        ("10159/lavadoras-y-secadoras", WASHING_MACHINE),
        ("10034/planchas", ACCESORIES),
        ("10050/secadores-de-pelo", ACCESORIES),
        ("10042/calefonts", WATER_HEATER),
        ("10040/enfriadores", SPLIT_AIR_CONDITIONER),
        ("10043/calienta-camas", ACCESORIES),
        ("10160/estufas", SPACE_HEATER),
        ("10046/calefactores-electricos", SPACE_HEATER),
        ("10041/ventiladores", ACCESORIES),
        ("10034/planchas", IRON),
        ("10050/secadores-de-pelo", HAIR_CARE),
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args):
        product_urls = []
        session = session_with_proxy(extra_args)
        category_id = url_extension.split("/")[0]
        url = f"https://www.sindelen.cl/digitag/category/products/{category_id}.json"
        response = session.get(url)
        products_data = json.loads(response.text)

        for product in products_data:
            product_urls.append(product["product_url"])

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        response = session.get(url)
        soup = BeautifulSoup(response.text, "lxml")

        key = soup.find("div", "wishlist-btn")["data-idproduct"]
        sku_container = soup.find("span", {"data-id-product": True})

        if sku_container:
            sku = re.search(
                r"addToCartCReferenceFull\('(.+)',", sku_container["onclick"]
            ).groups()[0]
        else:
            sku = soup.find("span", "sku").text.split()[-1]

        name = soup.find("h1", {"itemprop": "name"}).text.strip()
        stock = -1 if sku_container else 0
        price = Decimal(remove_words(soup.find("div", "current-price").text))
        description = html_to_markdown(soup.find("div", {"id": "digiResume"}).text)
        picture_urls = [
            img["data-image-large-src"]
            for img in soup.find("div", {"id": "slider-product-img-container"}).findAll(
                "img"
            )
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
            part_number=sku,
            sku=sku,
            picture_urls=picture_urls,
            description=description,
        )

        return [p]
