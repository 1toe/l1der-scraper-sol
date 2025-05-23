import logging
from bs4 import BeautifulSoup
from decimal import Decimal

from storescraper.categories import (
    STEREO_SYSTEM,
    HEADPHONES,
    NOTEBOOK,
    TABLET,
    POWER_SUPPLY,
    COMPUTER_CASE,
    RAM,
    MOTHERBOARD,
    PROCESSOR,
    VIDEO_CARD,
    STORAGE_DRIVE,
    EXTERNAL_STORAGE_DRIVE,
    SOLID_STATE_DRIVE,
    CPU_COOLER,
    KEYBOARD_MOUSE_COMBO,
    MOUSE,
    KEYBOARD,
    MONITOR,
    PRINTER,
    GAMING_CHAIR,
    UPS,
    WEARABLE,
    MEMORY_CARD,
    ALL_IN_ONE,
    PRINTER_SUPPLY,
)
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import html_to_markdown, remove_words, session_with_proxy


class Spider(StoreWithUrlExtensions):
    url_extensions = [
        ["257-parlantes", STEREO_SYSTEM],
        ["271-audio", STEREO_SYSTEM],
        ["23-audifonos", HEADPHONES],
        ["41-notebooks-portatiles", NOTEBOOK],
        ["25-tablets", TABLET],
        ["32-fuentes-de-poder", POWER_SUPPLY],
        ["31-gabinetes", COMPUTER_CASE],
        ["36-memorias-ram", RAM],
        ["29-placas-madre", MOTHERBOARD],
        ["28-procesadores", PROCESSOR],
        ["30-tarjetas-de-video", VIDEO_CARD],
        ["26-discos-duros", STORAGE_DRIVE],
        ["235-discos-duros-externo", EXTERNAL_STORAGE_DRIVE],
        ["44-discos-ssd", SOLID_STATE_DRIVE],
        ["34-refrigeracion", CPU_COOLER],
        ["57-kits-teclados-mouse", KEYBOARD_MOUSE_COMBO],
        ["55-mouse", MOUSE],
        ["242-mouse", MOUSE],
        ["56-teclados", KEYBOARD],
        ["21-monitores", MONITOR],
        ["49-multifuncionales", PRINTER],
        ["48-laser", PRINTER],
        ["50-tinta", PRINTER],
        ["59-sillas-gamer", GAMING_CHAIR],
        ["269-upsrespaldo-de-energia", UPS],
        ["273-smartwatch", WEARABLE],
        ["274-memoria-flashpendrive", MEMORY_CARD],
        ["40-pc-fijos", ALL_IN_ONE],
        ["246-tintas-y-toner", PRINTER_SUPPLY],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args=None):
        product_urls = []
        session = session_with_proxy(extra_args)

        page = 1
        while True:
            if page > 20:
                raise Exception("page overflow: " + url_extension)

            url_webpage = "https://www.spider.cl/{}?page={}".format(url_extension, page)
            data = session.get(url_webpage).text
            soup = BeautifulSoup(data, "lxml")
            product_containers = soup.findAll("article", "product-miniature")

            if not product_containers:
                if page == 1:
                    logging.warning("Empty category: " + url_extension)

                break

            for product_container in product_containers:
                product_url = product_container.find("a")["href"]
                product_urls.append(product_url)
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

        part_number = (
            soup.find("div", "product-additional-info")
            .findAll("span")[1]
            .text.split("Referencia: ")[1]
            .strip()
        )
        name = soup.find("h1", "product-detail-name").text.strip()
        key = soup.find("meta", {"property": "product:retailer_item_id"})["content"]

        if soup.find("div", "product-quantities"):
            stock = int(
                soup.find("div", "product-quantities").find("span")["data-stock"]
            )
        else:
            stock = 0

        offer_price = Decimal(
            remove_words(soup.find("div", "product-price").text).strip()
        )
        normal_price = Decimal(
            remove_words(
                soup.find("div", "methods_prices_box")
                .find("div", "others_methods_price")
                .text
            ).strip()
        )

        if soup.find("div", "MagicToolboxSelectorsContainer"):
            picture_containers = soup.find("div", "MagicToolboxSelectorsContainer")
        else:
            picture_containers = soup.find("div", "MagicToolboxMainContainer")

        if picture_containers:
            picture_urls = [
                tag["src"].replace("-small_default", "")
                for tag in picture_containers.findAll("img")
            ]
        else:
            picture_urls = []

        description = html_to_markdown(soup.find("div", {"id": "description"}).text)

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
            sku=key,
            part_number=part_number,
            picture_urls=picture_urls,
            description=description,
        )

        return [p]
