import json

from bs4 import BeautifulSoup
from decimal import Decimal

from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import session_with_proxy, html_to_markdown
from storescraper.categories import (
    ALL_IN_ONE,
    CPU_COOLER,
    HEADPHONES,
    KEYBOARD,
    KEYBOARD_MOUSE_COMBO,
    MEMORY_CARD,
    MONITOR,
    MOTHERBOARD,
    MOUSE,
    NOTEBOOK,
    POWER_SUPPLY,
    PRINTER,
    PROCESSOR,
    RAM,
    STEREO_SYSTEM,
    STORAGE_DRIVE,
    TABLET,
    TELEVISION,
    USB_FLASH_DRIVE,
    WEARABLE,
    PRINTER_SUPPLY,
)


class ShopBox(StoreWithUrlExtensions):
    url_extensions = [
        ["surface-arc", MOUSE],
        ["parlantes", STEREO_SYSTEM],
        ["parlantes-bluetooth", STEREO_SYSTEM],
        ["televisores", TELEVISION],
        ["audifonos", HEADPHONES],
        ["audifonos-accesorios-computacion", HEADPHONES],
        ["enfriamiento", CPU_COOLER],
        ["kit-mouse-y-teclado", KEYBOARD_MOUSE_COMBO],
        ["mouse", MOUSE],
        ["teclados-accesorios-computacion", KEYBOARD],
        ["discos-duros", STORAGE_DRIVE],
        ["pendrives", USB_FLASH_DRIVE],
        ["tarjetas-de-memoria", MEMORY_CARD],
        ["fuentes-de-poder", POWER_SUPPLY],
        ["memorias-ram", RAM],
        ["placas-madre", MOTHERBOARD],
        ["procesadores", PROCESSOR],
        ["all-in-one", ALL_IN_ONE],
        ["imac-escritorio", ALL_IN_ONE],
        ["monitores-escritorio", MONITOR],
        ["notebooks", NOTEBOOK],
        ["tablets", TABLET],
        ["impresoras-y-scanners", PRINTER],
        ["relojes", WEARABLE],
        ["cartuchos-de-toner-e-ink-jet", PRINTER_SUPPLY],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args):
        product_urls = []
        session = session_with_proxy(extra_args)
        page = 1

        while True:
            if page > 60:
                raise Exception("Page overflow: " + url_extension)

            url = f"https://www.shopbox.cl/product-category/{url_extension}/page/{page}"
            print(url)
            response = session.get(url)

            if response.status_code == 404:
                if page == 1:
                    raise Exception(f"Empty category: {url}")
                break

            soup = BeautifulSoup(response.text, "lxml")
            products = soup.findAll("div", "product")
            for product in products:
                product_url = product.find("a")["href"]
                product_urls.append(product_url)

            page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        soup = BeautifulSoup(session.get(url).text, "lxml")
        products_data_container = soup.findAll(
            "script", {"type": "application/ld+json"}
        )

        if len(products_data_container) < 2:
            return []

        products_data = json.loads(products_data_container[1].text)
        key = soup.find("link", {"rel": "shortlink"})["href"].split("=")[-1]
        offers = products_data["offers"]

        assert len(offers) == 1

        offer = offers[0]
        original_name = products_data["name"]
        name = original_name[:256]
        sku = str(products_data["sku"])
        prices_container = soup.find("table", {"id": "tabla-precios"})

        if not prices_container:
            return []

        prices = [
            int(price.text.replace(".", "").replace("$", ""))
            for price in prices_container.findAll(
                "span", "woocommerce-Price-amount amount"
            )
        ]
        prices = sorted(prices)[:2]
        offer_price = Decimal(prices[0])
        normal_price = Decimal(prices[1])

        if normal_price > Decimal("100000000") or offer_price > Decimal("100000000"):
            return []

        stock = -1 if offer["availability"] == "http://schema.org/InStock" else 0
        picture_urls = [
            tag.find("a")["href"]
            for tag in soup.findAll("div", "woocommerce-product-gallery__image")
        ]
        description = html_to_markdown(products_data["description"])

        if "reacondicionado" in original_name.lower():
            condition = "https://schema.org/Refurbished"
        elif "segunda mano" in original_name.lower():
            condition = "https://schema.org/UsedCondition"
        elif "caja abierta" in original_name.lower():
            condition = "https://schema.org/OpenBoxCondition"
        else:
            condition = "https://schema.org/NewCondition"

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
            condition=condition,
            part_number=sku,
        )

        return [p]
