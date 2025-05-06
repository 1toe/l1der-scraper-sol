from decimal import Decimal

from bs4 import BeautifulSoup

from storescraper.categories import (
    ALL_IN_ONE,
    CELL,
    COMPUTER_CASE,
    CPU_COOLER,
    EXTERNAL_STORAGE_DRIVE,
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
    SOLID_STATE_DRIVE,
    STEREO_SYSTEM,
    TABLET,
    TELEVISION,
    UPS,
    USB_FLASH_DRIVE,
    VIDEO_CARD,
    VIDEO_GAME_CONSOLE,
    ACCESORIES,
    PRINTER_SUPPLY,
)
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import html_to_markdown, remove_words, session_with_proxy


class TiShop(StoreWithUrlExtensions):
    url_extensions = [
        ["113?q[navbar_items_id_eq_any][]=114", ALL_IN_ONE],
        ["113?q[navbar_items_id_eq_any][]=115", NOTEBOOK],
        ["113?q[navbar_items_id_eq_any][]=117", TABLET],
        ["46?q[navbar_items_id_eq_any][]=119", EXTERNAL_STORAGE_DRIVE],
        ["46?q[navbar_items_id_eq_any][]=47", SOLID_STATE_DRIVE],
        ["46?q[navbar_items_id_eq_any][]=121", USB_FLASH_DRIVE],
        ["46?q[navbar_items_id_eq_any][]=49", MEMORY_CARD],
        ["56?q[navbar_items_id_eq_any][]=55", KEYBOARD],
        ["56?q[navbar_items_id_eq_any][]=57", MOUSE],
        ["56?q[navbar_items_id_eq_any][]=58", KEYBOARD_MOUSE_COMBO],
        ["59?q[navbar_items_id_eq_any][]=35", PRINTER],
        ["59?q[navbar_items_id_eq_any][]=129", PRINTER],
        ["76?q[navbar_items_id_eq_any][]=77", UPS],
        ["79", CELL],
        ["132?q[navbar_items_id_eq_any][]=69", VIDEO_GAME_CONSOLE],
        ["145?q[navbar_items_id_eq_any][]=146", MONITOR],
        ["145?q[navbar_items_id_eq_any][]=148", TELEVISION],
        ["63?q[navbar_items_id_eq_any][]=45", STEREO_SYSTEM],
        ["63?q[navbar_items_id_eq_any][]=54", HEADPHONES],
        ["50", RAM],
        ["84", CPU_COOLER],
        ["98", COMPUTER_CASE],
        ["51", MOTHERBOARD],
        ["107", POWER_SUPPLY],
        ["52", PROCESSOR],
        ["81", VIDEO_CARD],
        ["60?q[navbar_items_id_eq_any][]=72", ACCESORIES],
        ["59?q[navbar_items_id_eq_any][]=37", PRINTER_SUPPLY],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args=None):
        session = session_with_proxy(extra_args)
        previous_urls = None
        product_urls = []
        page = 1

        while True:
            if page > 50:
                raise Exception(f"page overflow: {url_extension}")

            separator = "&" if "?" in url_extension else "?"
            url_webpage = (
                f"https://tishop.cl/categories/{url_extension}{separator}page={page}"
            )
            print(url_webpage)

            response = session.get(url_webpage)
            soup = BeautifulSoup(response.text, "lxml")
            product_containers = soup.findAll("article", "group/item")
            urls = set(
                f"https://tishop.cl{tag.find('a')['href']}"
                for tag in product_containers
            )

            if urls == previous_urls:
                break

            product_urls.extend(urls)
            previous_urls = urls
            page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        session = session_with_proxy(extra_args)
        response = session.get(url)

        if response.status_code == 404:
            return []

        soup = BeautifulSoup(response.text, "lxml")

        product_data_container = soup.findAll("section")[1]
        product_data_tags = product_data_container.findAll("div")
        brand = soup.find("meta", {"name": "author"})["content"]
        model_name = product_data_tags[1].text.strip()
        name = f"{brand} {model_name}"
        sku = product_data_tags[2].text.strip()
        key = soup.find("input", {"id": "line_item_product_id"}).get("value")

        normal_price = None
        offer_price = None

        for i, product_data_tag in enumerate(product_data_tags):
            tag_text = product_data_tag.text.strip().lower()

            if tag_text == "por transferencia":
                offer_price = Decimal(
                    remove_words(product_data_tags[i - 1].text.strip().lower())
                )
            elif tag_text == "otros medios de pago":
                normal_price = Decimal(
                    remove_words(product_data_tags[i - 1].text.strip().lower())
                )

        if normal_price == 0:
            return []

        stock = -1 if soup.find("form", {"id": "add_to_cart_form"}) else 0
        picture_urls_container = soup.find("div", "main-carousel")
        picture_urls = [img["src"] for img in picture_urls_container.findAll("img")]
        description = html_to_markdown(soup.find("div", "product-data").text)

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
            part_number=sku,
            picture_urls=picture_urls,
            description=description,
        )

        return [p]
