import logging
from bs4 import BeautifulSoup
from storescraper.categories import (
    ALL_IN_ONE,
    CPU_COOLER,
    GAMING_CHAIR,
    KEYBOARD_MOUSE_COMBO,
    POWER_SUPPLY,
    TABLET,
    VIDEO_CARD,
    SOLID_STATE_DRIVE,
    COMPUTER_CASE,
    PROCESSOR,
    RAM,
    MONITOR,
    HEADPHONES,
    NOTEBOOK,
    USB_FLASH_DRIVE,
    STEREO_SYSTEM,
    PRINTER,
    PRINTER_SUPPLY,
    ACCESORIES,
    UPS,
)
from storescraper.utils import session_with_proxy
from storescraper.stores.mercado_libre_chile import MercadoLibreChile


class Tecnocam(MercadoLibreChile):
    @classmethod
    def categories(cls):
        return [
            ALL_IN_ONE,
            CPU_COOLER,
            GAMING_CHAIR,
            KEYBOARD_MOUSE_COMBO,
            POWER_SUPPLY,
            TABLET,
            VIDEO_CARD,
            SOLID_STATE_DRIVE,
            COMPUTER_CASE,
            PROCESSOR,
            RAM,
            MONITOR,
            HEADPHONES,
            NOTEBOOK,
            USB_FLASH_DRIVE,
            STEREO_SYSTEM,
            PRINTER,
            PRINTER_SUPPLY,
            ACCESORIES,
            UPS,
        ]

    @classmethod
    def discover_urls_for_category(cls, category, extra_args=None):
        url_extensions = [
            ["computacion/notebooks-accesorios/notebooks", NOTEBOOK],
            ["computacion/notebooks-accesorios/accesorios-notebooks", ACCESORIES],
            ["computacion/laptops-accesorios/repuestos", ACCESORIES],
            ["computacion/componentes-pc/tarjetas", VIDEO_CARD],
            [
                "computacion/componentes-pc/discos-accesorios/discos-duros-ssds",
                SOLID_STATE_DRIVE,
            ],
            ["computacion/componentes-pc/discos-accesorios/accesorios", ACCESORIES],
            ["computacion/componentes-pc/memorias-ram", RAM],
            ["computacion/componentes-pc/procesadores", PROCESSOR],
            ["computacion/componentes-pc/fuentes-alimentacion", POWER_SUPPLY],
            ["computacion/componentes-pc/gabinetes-soportes-pc", COMPUTER_CASE],
            ["computacion/componentes-pc/refrigeracion", CPU_COOLER],
            ["computacion/accesorios-pc-gaming/audifonos", HEADPHONES],
            ["computacion/accesorios-pc-gaming/sillas-gamer", GAMING_CHAIR],
            ["computacion/almacenamiento/pen-drives", USB_FLASH_DRIVE],
            ["computacion/estabilizadores-ups", UPS],
            ["computacion/perifericos-accesorios/cables-hubs-usb", ACCESORIES],
            ["computacion/impresion/insumos-impresion", PRINTER_SUPPLY],
            ["computacion/impresion/impresoras", PRINTER],
            ["computacion/impresion/accesorios", ACCESORIES],
            ["computacion/limpieza-cuidado-pcs", ACCESORIES],
            ["pc-escritorio-all-in-one", ALL_IN_ONE],
            ["computacion/monitores-accesorios/monitores", MONITOR],
            ["perifericos-pc-mouses-teclados", KEYBOARD_MOUSE_COMBO],
            ["computacion/tablets-accesorios/accesorios", ACCESORIES],
            ["computacion/tablets-accesorios/tablets", TABLET],
            ["electronica-audio-video/audio/audio-portatil-accesorios", STEREO_SYSTEM],
            ["electronica-audio-video/audio/audifonos", HEADPHONES],
            ["electronica-audio-video/audio/parlantes-subwoofers", STEREO_SYSTEM],
            ["electronica-audio-video/accesorios-audio-video", ACCESORIES],
            ["electronica-audio-video/cables", ACCESORIES],
            ["celulares-telefonia/accesorios-celulares/cargadores", ACCESORIES],
            ["celulares-telefonia/accesorios-celulares/manos-libres", HEADPHONES],
            ["celulares-telefonia/accesorios-celulares/parlantes", STEREO_SYSTEM],
            ["celulares-telefonia/accesorios-celulares/baterias", ACCESORIES],
            ["celulares-telefonia/accesorios-celulares/cables-datos", ACCESORIES],
        ]
        session = session_with_proxy(extra_args)
        products_urls = []

        for url_extension, local_category in url_extensions:
            if local_category != category:
                continue

            index = 1

            while True:
                if index > 1000:
                    raise Exception("page overflow: " + url_extension)

                url_webpage = f"https://www.tecnocam.cl/listado/{url_extension}/_Desde_{index}_NoIndex_True"
                print(url_webpage)
                response = session.get(url_webpage)
                soup = BeautifulSoup(response.text, "lxml")
                product_containers = soup.find_all("li", "ui-search-layout__item")

                if not product_containers:
                    if index == 1:
                        logging.warning("Empty category: " + url_extension)
                    break

                for container in product_containers:
                    products_url = (
                        container.find("a")["href"].split("#")[0].split("?")[0]
                    )
                    products_urls.append(products_url)

                index += 50

        return products_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        return cls._products_for_url_with_custom_price(
            url, category=category, extra_args=extra_args
        )
