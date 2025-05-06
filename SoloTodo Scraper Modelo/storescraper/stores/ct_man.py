import logging
import urllib
from decimal import Decimal

from bs4 import BeautifulSoup

from storescraper.categories import (
    PRINTER,
    KEYBOARD,
    HEADPHONES,
    GAMING_CHAIR,
    COMPUTER_CASE,
    RAM,
    POWER_SUPPLY,
    PROCESSOR,
    MOTHERBOARD,
    VIDEO_CARD,
    EXTERNAL_STORAGE_DRIVE,
    USB_FLASH_DRIVE,
    MONITOR,
    KEYBOARD_MOUSE_COMBO,
    NOTEBOOK,
    SOLID_STATE_DRIVE,
    ALL_IN_ONE,
    TELEVISION,
    CELL,
    VIDEO_GAME_CONSOLE,
    MOUSE,
    CPU_COOLER,
    STORAGE_DRIVE,
    MEMORY_CARD,
    TABLET,
    UPS,
    STEREO_SYSTEM,
    WEARABLE,
    ACCESORIES,
    PRINTER_SUPPLY,
    PROJECTOR,
)
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import session_with_proxy, remove_words, html_to_markdown


class CtMan(StoreWithUrlExtensions):
    url_extensions = [
        ["types/notebooks", NOTEBOOK],
        ["types/memorias-ram-para-laptops", RAM],
        ["types/memorias-ram", RAM],
        ["types/memoria-ram-server", RAM],
        ["types/all-in-one", ALL_IN_ONE],
        ["types/gabinetes", COMPUTER_CASE],
        ["types/impresoras", PRINTER],
        ["types/teclados", KEYBOARD],
        ["types/teclados-fisicos", KEYBOARD],
        ["types/audifonos", HEADPHONES],
        ["types/impresoras-a-color", PRINTER],
        ["types/coolers-para-pc", CPU_COOLER],
        ["types/fuentes-de-poder", POWER_SUPPLY],
        ["types/tarjetas-de-video", VIDEO_CARD],
        ["types/procesadores", PROCESSOR],
        ["types/placas-madre", MOTHERBOARD],
        ["types/packs", PROCESSOR],
        ["types/discos-duros-externos", EXTERNAL_STORAGE_DRIVE],
        ["types/ssds-externos", EXTERNAL_STORAGE_DRIVE],
        ["types/ssd", SOLID_STATE_DRIVE],
        ["types/pen-drives", USB_FLASH_DRIVE],
        ["types/monitores", MONITOR],
        ["types/televisores", TELEVISION],
        ["types/celulares-y-smartphones", CELL],
        ["types/fuentes-de-alimentacion", POWER_SUPPLY],
        ["types/sillas-gamer", GAMING_CHAIR],
        ["types/gabinetes", COMPUTER_CASE],
        ["types/notebooks", NOTEBOOK],
        ["types/kits-de-mouse-y-teclado", KEYBOARD_MOUSE_COMBO],
        ["types/consolas-de-videojuegos", VIDEO_GAME_CONSOLE],
        ["types/mouse", MOUSE],
        ["types/coolers-para-pc", CPU_COOLER],
        ["types/disco-duro", STORAGE_DRIVE],
        ["types/tarjeta-de-memoria-flash", MEMORY_CARD],
        ["types/tablets", TABLET],
        ["types/ups", UPS],
        ["types/parlantes", STEREO_SYSTEM],
        ["types/reloj-inteligente", WEARABLE],
        ["types/macbooks", NOTEBOOK],
        ["types/ipads", TABLET],
        ["types/iphone", CELL],
        ["types/watch", WEARABLE],
        ["types/botella-de-tinta", PRINTER_SUPPLY],
        ["types/toner", PRINTER_SUPPLY],
        ["types/cartucho-de-tinta", PRINTER_SUPPLY],
        ["collections/electrodomesticos", ACCESORIES],
        ["types/proyectores", PROJECTOR],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args=None):
        session = session_with_proxy(extra_args)
        session.headers["User-Agent"] = "SoloTodoBot"
        product_urls = []
        page = 1
        while True:
            if page > 25:
                raise Exception("page overflow: " + url_extension)
            url_webpage = "https://www.ctman.cl/{}/" "{}".format(url_extension, page)
            print(url_webpage)
            response = session.get(url_webpage)
            soup = BeautifulSoup(response.text, "lxml")
            product_containers = soup.findAll("div", "product-item")
            if not product_containers:
                if page == 1:
                    logging.warning("Empty category: " + url_extension)
                break
            for container in product_containers:
                product_url = container.find("a")["href"]
                product_urls.append(product_url)
            page += 1
        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        session.headers["User-Agent"] = "SoloTodoBot"
        response = session.get(url)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, "lxml")
        key_tag = soup.find("div", "title-description").find(
            "input", {"name": "cart_item[variant_id]"}
        )

        if not key_tag:
            return []

        key = key_tag["value"]
        name = soup.find("h1", "product-name").text.strip()
        sku = soup.find("div", "sku").text.split(":")[1].strip()
        description = html_to_markdown(str(soup.find("div", "product-description")))
        price_tag = soup.find("big", "product-price").find("span", "bootic-price")
        price = Decimal(remove_words(price_tag.text))

        add_to_cart_tag = soup.find("input", value="Agregar al carro")

        if add_to_cart_tag:
            stock = -1
        else:
            stock = 0

        picture_urls = []
        for i in soup.findAll("li", "product-asset"):
            parsed_url = urllib.parse.urlparse(i.find("a")["href"])
            picture_url = parsed_url._replace(
                path=urllib.parse.quote(parsed_url.path)
            ).geturl()
            picture_urls.append(picture_url)

        part_number_tag = soup.find("p", "part-number")
        if part_number_tag:
            part_number = soup.find("p", "part-number").contents[1].strip()
        else:
            part_number = None

        special_tags = soup.findAll("div", "special-tags")

        if special_tags:
            condition = "https://schema.org/RefurbishedCondition"
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
            price,
            price,
            "CLP",
            sku=sku,
            picture_urls=picture_urls,
            description=description,
            part_number=part_number,
            condition=condition,
        )
        return [p]
