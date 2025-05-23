import logging

from bs4 import BeautifulSoup
from decimal import Decimal

from storescraper.categories import (
    GAMING_CHAIR,
    USB_FLASH_DRIVE,
    EXTERNAL_STORAGE_DRIVE,
    MEMORY_CARD,
    CELL,
    CPU_COOLER,
    CASE_FAN,
    VIDEO_CARD,
    PROCESSOR,
    MONITOR,
    MOTHERBOARD,
    RAM,
    STORAGE_DRIVE,
    SOLID_STATE_DRIVE,
    POWER_SUPPLY,
    COMPUTER_CASE,
    MOUSE,
    KEYBOARD,
    KEYBOARD_MOUSE_COMBO,
    HEADPHONES,
    STEREO_SYSTEM,
    NOTEBOOK,
    PRINTER_SUPPLY,
)
from storescraper.product import Product
from storescraper.store import Store
from storescraper.utils import remove_words, html_to_markdown, session_with_proxy


class AllTec(Store):
    preferred_products_for_url_concurrency = 3

    @classmethod
    def categories(cls):
        return [
            VIDEO_CARD,
            PROCESSOR,
            MONITOR,
            MOTHERBOARD,
            RAM,
            STORAGE_DRIVE,
            SOLID_STATE_DRIVE,
            POWER_SUPPLY,
            COMPUTER_CASE,
            CPU_COOLER,
            MOUSE,
            KEYBOARD,
            KEYBOARD_MOUSE_COMBO,
            HEADPHONES,
            STEREO_SYSTEM,
            NOTEBOOK,
            GAMING_CHAIR,
            USB_FLASH_DRIVE,
            EXTERNAL_STORAGE_DRIVE,
            MEMORY_CARD,
            CELL,
            CASE_FAN,
            PRINTER_SUPPLY,
        ]

    @classmethod
    def discover_urls_for_category(cls, category, extra_args=None):
        base_url = "https://www.alltec.cl/"

        category_urls = [
            ["16-gabinetes", COMPUTER_CASE],
            ["18-fuentes-de-poder", POWER_SUPPLY],
            ["17-placas-madre", MOTHERBOARD],
            ["20-procesadores", PROCESSOR],
            ["19-memorias", RAM],
            ["100-sodimm", RAM],
            ["24-mouse", MOUSE],
            ["43-impresoras", "Printer"],
            ["55-tarjetas-de-video", VIDEO_CARD],
            ["23-teclados", KEYBOARD],
            ["62-gamer", KEYBOARD],
        ]

        url_extensions = [
            ["33-mecanicos-rigidos", STORAGE_DRIVE],
            ["34-ssd", SOLID_STATE_DRIVE],
            ["27-monitores", MONITOR],
            ["93-cpu-cooler", CPU_COOLER],
            ["92-water-cooling", CPU_COOLER],
            ["25-auriculares", HEADPHONES],
            ["110-pc", HEADPHONES],
            ["111-consolas", HEADPHONES],
            ["26-parlantes", STEREO_SYSTEM],
            ["65-notebook-tablet", NOTEBOOK],
            ["96-sillas", GAMING_CHAIR],
            ["35-flashpendrive", USB_FLASH_DRIVE],
            ["58-pendrive", USB_FLASH_DRIVE],
            ["95-externos-usb", EXTERNAL_STORAGE_DRIVE],
            ["59-memorias-flash-microsdsdcompac-flash", MEMORY_CARD],
            ["74-smartphone-smartwatch-smartband", CELL],
            ["91-chassis-fan-ventiladores", CASE_FAN],
            ["45-tinta", PRINTER_SUPPLY],
        ]

        session = session_with_proxy(extra_args)
        session.headers["User-Agent"] = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36"
        )
        for category_path, local_category in category_urls:
            if local_category != category:
                continue

            url_extensions.append((category_path, category))

            category_url = base_url + category_path
            soup = BeautifulSoup(session.get(category_url).text, "lxml")

            subcategory_containers = soup.findAll("div", "subcategory-image")

            if not subcategory_containers:
                logging.warning("Empty category: " + category_url)
                continue

            for container in subcategory_containers:
                subcategory_url = container.find("a")["href"].replace(base_url, "")
                url_extensions.append((subcategory_url, category))

        product_urls = []

        for subcategory_path, local_category in url_extensions:
            if local_category != category:
                continue

            page = 1

            while True:
                subcategory_url = "{}{}?p={}".format(base_url, subcategory_path, page)
                print(subcategory_url)
                response = session.get(subcategory_url)

                if response.url != subcategory_url:
                    break

                soup = BeautifulSoup(response.text, "lxml")
                link_containers = soup.findAll("div", "product-container")

                if not link_containers and page == 1:
                    logging.warning("Empty subcategory: " + subcategory_url)
                    break

                for link_container in link_containers:
                    product_url = link_container.find("a")["href"]
                    product_urls.append(product_url)

                page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        session = session_with_proxy(extra_args)
        session.headers["User-Agent"] = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36"
        )
        soup = BeautifulSoup(session.get(url).text, "lxml")

        name = soup.find("h1", {"itemprop": "name"}).text.strip()
        sku = soup.find("input", {"name": "id_product"})["value"].strip()

        part_number = None
        part_number_container = soup.find("span", {"itemprop": "sku"})
        if part_number_container.text:
            part_number = part_number_container["content"].strip()

        condition = soup.find("link", {"itemprop": "itemCondition"})

        if condition:
            condition = condition["href"].strip()
        else:
            condition = "https://schema.org/NewCondition"

        description = "{}\n\n{}".format(
            html_to_markdown(str(soup.find("div", {"itemprop": "description"}))),
            html_to_markdown(str(soup.find("section", "page-product-box"))),
        )

        add_to_card_button = soup.find("p", {"id": "add_to_cart"})

        stock = -1
        try:
            if "unvisible" in add_to_card_button.parent["class"]:
                stock = 0
        except KeyError:
            pass

        if "NOTA: " in description:
            stock = 0

        offer_price_string = soup.find("span", {"id": "our_price_display"}).text
        offer_price = Decimal(remove_words(offer_price_string))

        normal_price_string = soup.find("span", {"id": "unit_price_display"})

        if normal_price_string:
            normal_price = Decimal(remove_words(normal_price_string.text))
        else:
            normal_price = offer_price

        if offer_price > normal_price:
            offer_price = normal_price

        picture_urls = [x["href"] for x in soup.findAll("a", "fancybox")]

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
            part_number=part_number,
            condition=condition,
            description=description,
            picture_urls=picture_urls,
        )

        return [p]
