import logging

from bs4 import BeautifulSoup
from storescraper.categories import (
    NOTEBOOK,
    CPU_COOLER,
    STORAGE_DRIVE,
    VIDEO_CARD,
    MOUSE,
    KEYBOARD,
    KEYBOARD_MOUSE_COMBO,
    MONITOR,
    HEADPHONES,
    USB_FLASH_DRIVE,
    CELL,
)
from storescraper.stores.mercado_libre_chile import MercadoLibreChile
from storescraper.utils import session_with_proxy


class MegaOfertas(MercadoLibreChile):
    @classmethod
    def categories(cls):
        return [
            NOTEBOOK,
            CPU_COOLER,
            STORAGE_DRIVE,
            VIDEO_CARD,
            MOUSE,
            KEYBOARD_MOUSE_COMBO,
            KEYBOARD_MOUSE_COMBO,
            MONITOR,
            HEADPHONES,
            USB_FLASH_DRIVE,
            CELL,
        ]

    @classmethod
    def discover_urls_for_category(cls, category, extra_args=None):
        url_extensions = [
            ("notebooks-accesorios", NOTEBOOK),
            ("computacion/componentes-pc/refrigeracion", CPU_COOLER),
            ("computacion/componentes-pc/discos-accesorios", STORAGE_DRIVE),
            ("computacion/componentes-pc/tarjetas", VIDEO_CARD),
            ("computacion/perifericos-accesorios/mouses", MOUSE),
            ("computacion/perifericos-accesorios/teclados", KEYBOARD),
            ("mouses-teclados-controles-kits-mouse-teclado", KEYBOARD_MOUSE_COMBO),
            ("computacion/monitores-accesorios", MONITOR),
            ("computacion/accesorios-pc-gaming", HEADPHONES),
            ("computacion/almacenamiento", USB_FLASH_DRIVE),
            ("consolas-videojuegos/accesorios-consolas", HEADPHONES),
            ("consolas-videojuegos/accesorios-pc-gaming", HEADPHONES),
            ("electronica-audio-video/audio", HEADPHONES),
            ("celulares-telefonia", CELL),
        ]
        session = session_with_proxy(extra_args)
        product_urls = []

        for url_extension, local_category in url_extensions:
            if local_category != category:
                continue
            page = 1

            while True:
                if page > 10:
                    raise Exception("Page overflow: " + url_extension)

                index = str(50 * (page - 1) + 1)
                url_webpage = f"https://www.megaofertascg.com/listado/{url_extension}/_Desde_{index}_NoIndex_True"
                print(url_webpage)
                data = session.get(url_webpage).text
                soup = BeautifulSoup(data, "lxml")
                product_containers = soup.findAll("li", "ui-search-layout__item")

                if not product_containers:
                    if page == 1:
                        logging.warning("Empty category: " + url_extension)
                    break

                for container in product_containers:
                    link_container = container.find(
                        "a", "poly-component__title"
                    ) or container.find("a", "ui-search-link")
                    product_url = link_container["href"].split("#")[0].split("?")[0]
                    product_urls.append(product_url)

                page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        return cls._products_for_url_with_custom_price(
            url, category=category, extra_args=extra_args
        )
