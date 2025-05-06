import html
import json
import logging
import re
from decimal import Decimal

from bs4 import BeautifulSoup

from storescraper.categories import (
    GAMING_CHAIR,
    MOUSE,
    NOTEBOOK,
    TABLET,
    CELL,
    PRINTER,
    ALL_IN_ONE,
    TELEVISION,
    HEADPHONES,
    VIDEO_CARD,
    COMPUTER_CASE,
    RAM,
    MONITOR,
    VIDEO_GAME_CONSOLE,
    PRINTER_SUPPLY,
    ACCESORIES,
    PROCESSOR,
    PROJECTOR,
    STORAGE_DRIVE,
    STEREO_SYSTEM,
    POWER_SUPPLY,
    UPS,
    SOLID_STATE_DRIVE,
    EXTERNAL_STORAGE_DRIVE,
    CPU_COOLER,
    USB_FLASH_DRIVE,
    MEMORY_CARD,
    KEYBOARD,
    KEYBOARD_MOUSE_COMBO,
    WEARABLE,
)
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import session_with_proxy, html_to_markdown


class BookComputer(StoreWithUrlExtensions):
    url_extensions = [
        ["gamer", NOTEBOOK],
        ["notebook-y-desktop", NOTEBOOK],
        ["computadores", NOTEBOOK],
        ["portatiles", NOTEBOOK],
        ["computadores-de-mesa", NOTEBOOK],
        ["accesorios-para-portatiles", ACCESORIES],
        ["servidores", NOTEBOOK],
        ["accesorios-para-servidores", ACCESORIES],
        ["software-para-servidores-enterprise", ACCESORIES],
        ["computadoras-handheld", NOTEBOOK],
        ["sistema-operativo", ACCESORIES],
        ["partes-y-piezas", PROCESSOR],
        ["monitores-y-proyectores", MONITOR],
        ["proyectores", PROJECTOR],
        ["monitores", MONITOR],
        ["impresoras-y-escaneres", PRINTER],
        ["impresoras-para-recibos", PRINTER],
        ["impresoras-de-etiquetas", PRINTER],
        ["impresoras-laser", PRINTER],
        ["impresoras-ink-jet", PRINTER],
        ["impresoras-fotograficas", PRINTER],
        ["impresoras-multifuncionales", PRINTER],
        ["escaneres", PRINTER],
        ["suministros-y-partes-de-mantenimiento", PRINTER_SUPPLY],
        ["cartuchos-de-toner-e-ink-jet", PRINTER_SUPPLY],
        ["cintas-de-impresion", PRINTER_SUPPLY],
        ["cintas-de-almacenamiento", STORAGE_DRIVE],
        ["consumibles-y-media", ACCESORIES],
        ["papel", ACCESORIES],
        ["tableta", TABLET],
        ["tabletas-digitales", TABLET],
        ["estuches-para-tablets", ACCESORIES],
        ["accesorios-para-tablets", ACCESORIES],
        ["otros-accesorios", ACCESORIES],
        ["sillas", GAMING_CHAIR],
        ["consolas", VIDEO_GAME_CONSOLE],
        ["videojuegos", ACCESORIES],
        ["controles", ACCESORIES],
        ["audio-y-video", ACCESORIES],
        ["camaras-videocamaras", ACCESORIES],
        ["camaras", ACCESORIES],
        ["reproductores-de-streaming-media", ACCESORIES],
        ["camaras-web", ACCESORIES],
        ["video-conferencia", STEREO_SYSTEM],
        ["camaras-analogas", ACCESORIES],
        ["camaras-de-red", ACCESORIES],
        ["dvrs", ACCESORIES],
        ["nvrs", ACCESORIES],
        ["kits", ACCESORIES],
        ["televisores", TELEVISION],
        ["cables", ACCESORIES],
        ["cables-y-adaptadores", ACCESORIES],
        ["accesorios-para-cableo", ACCESORIES],
        ["sistemas-de-audio-para-evacuacion", STEREO_SYSTEM],
        ["auriculares-y-manos-libres", HEADPHONES],
        ["parlantes-/-bocinas/cornetas-inteligentes", STEREO_SYSTEM],
        ["auriculares", HEADPHONES],
        ["microfonos", ACCESORIES],
        ["parlantes-/-bocinas/cornetas", STEREO_SYSTEM],
        ["tarjetas-de-sonido", ACCESORIES],
        ["componentes-informaticos", PROCESSOR],
        ["tarjetas", VIDEO_CARD],
        ["adaptadores-y-controladoras", ACCESORIES],
        ["aplicaciones-para-negocio-y-oficina", ACCESORIES],
        ["almacenamiento", STORAGE_DRIVE],
        ["procesadores", PROCESSOR],
        ["fuentes-de-poder", POWER_SUPPLY],
        ["ups/respaldo-de-energia", UPS],
        ["cajas/gabinetes", COMPUTER_CASE],
        ["discos-de-estado-solido", SOLID_STATE_DRIVE],
        ["discos-duros-internos", STORAGE_DRIVE],
        ["discos-duros-externos", EXTERNAL_STORAGE_DRIVE],
        ["ventiladores-y-sistemas-de-enfriamiento", CPU_COOLER],
        ["almacenamiento-de-redes-nas", STORAGE_DRIVE],
        ["otros", ACCESORIES],
        ["celulares", CELL],
        ["celulares-desbloqueados", CELL],
        ["estuches-para-celulares", ACCESORIES],
        ["redes", ACCESORIES],
        ["hubs-switches", ACCESORIES],
        ["placas-y-soported-de-pared", ACCESORIES],
        ["paneles-gabinetes-y-cajas-de-redes", ACCESORIES],
        ["perifericos", MOUSE],
        ["conectores", ACCESORIES],
        ["herramientas-y-equipo-de-herramientas", ACCESORIES],
        ["paneles", ACCESORIES],
        ["sistemas-avanzados-de-asistencia-al-conductor", ACCESORIES],
        ["puntos-de-acceso", ACCESORIES],
        ["antenas", ACCESORIES],
        ["puentes-y-enrutadores", ACCESORIES],
        ["scooters", ACCESORIES],
        ["memorias", RAM],
        ["unidades-flash-usb", USB_FLASH_DRIVE],
        ["memoria-de-lectores-de-medios", ACCESORIES],
        ["tarjetas-de-memoria-flash", MEMORY_CARD],
        ["modulos-ram-genericos", RAM],
        ["modulos-ram-propietarios", RAM],
        ["tarjetas-de-expansion-de-memoria", RAM],
        ["modulos-de-expansion", RAM],
        ["accesorios-para-computadores", ACCESORIES],
        ["maletines", ACCESORIES],
        ["usb-hubs", ACCESORIES],
        ["software", ACCESORIES],
        ["mouse-pads-y-wrist-pads", ACCESORIES],
        ["baterias-y-cargadores", ACCESORIES],
        ["maletines-para-notebooks", ACCESORIES],
        ["escritorios", ACCESORIES],
        ["estantes", ACCESORIES],
        ["mochilas", ACCESORIES],
        ["ratones", MOUSE],
        ["teclados-y-teclados-de-numeros", KEYBOARD],
        ["protectores", ACCESORIES],
        ["combos-de-teclado-y-raton", KEYBOARD_MOUSE_COMBO],
        ["muebles", ACCESORIES],
        ["accesorios", ACCESORIES],
        ["voltaje/reguladores-en-linea", UPS],
        ["seguridad", ACCESORIES],
        ["tecnologia-portatil", ACCESORIES],
        ["cuidado-personal", ACCESORIES],
        ["climatizacion", ACCESORIES],
        ["iluminacion", ACCESORIES],
        ["relojes", WEARABLE],
        ["administracion-de-energia", UPS],
        ["escaneres-de-codigo-de-barras", ACCESORIES],
        ["outlet", ACCESORIES],
        ["audifonos", HEADPHONES],
        ["smartphone", CELL],
        ["smartwatch", WEARABLE],
        ["outlet-1", ACCESORIES],
        ["tablet-1", TABLET],
        ["outlet/impresoras", PRINTER],
        ["outlet/all-in-one", ALL_IN_ONE],
        ["outlet/monitores", MONITOR],
        ["outlet/consolas", VIDEO_GAME_CONSOLE],
        ["outlet/accesorios", ACCESORIES],
        ["kospet", ACCESORIES],
        ["chuwi", ACCESORIES],
        ["bitfenix", ACCESORIES],
        ["thunderobot", ACCESORIES],
        ["camaras-de-seguridad", ACCESORIES],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args=None):
        session = session_with_proxy(extra_args)
        product_urls = []
        page = 1
        while True:
            if page > 30:
                raise Exception("page overflow: " + url_extension)
            url_webpage = "https://www.bookcomputer.cl/{}?page={}".format(
                url_extension, page
            )
            print(url_webpage)
            data = session.get(url_webpage).text
            soup = BeautifulSoup(data, "lxml")
            product_containers = soup.findAll("div", "product-block")
            if not product_containers:
                if page == 1:
                    logging.warning("Empty category: " + url_extension)
                break
            for container in product_containers:
                product_url = container.find("a")["href"]
                product_urls.append("https://www.bookcomputer.cl" + product_url)
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
        description = html_to_markdown(str(soup.find("div", "description")))

        if soup.find("select", "form-control"):
            products = []
            variations = json.loads(
                re.search(r"var productInfo = (.*);", response.text).groups()[0]
            )
            for product in variations:
                name = soup.find("h1", "page-header").text

                if "REACONDICIONADO" in name.upper():
                    condition = "https://schema.org/RefurbishedCondition"
                else:
                    condition = "https://schema.org/NewCondition"

                sku = str(product["variant"]["id"])
                price = Decimal(product["variant"]["price"])

                if "PEDIDO" in name.upper():
                    stock = 0
                else:
                    stock = product["variant"]["stock"]

                picture_urls = [
                    tag["src"]
                    for tag in soup.find("div", "product-images").findAll("img")
                ]
                p = Product(
                    name,
                    cls.__name__,
                    category,
                    url,
                    url,
                    sku,
                    stock,
                    price,
                    price,
                    "CLP",
                    sku=sku,
                    picture_urls=picture_urls,
                    description=description,
                    condition=condition,
                )
                products.append(p)
            return products
        else:
            json_info = json.loads(
                soup.find("script", {"type": "application/ld+json"}).text, strict=False
            )
            if "sku" not in json_info:
                sku = soup.find("form", "product-form")["id"].split("-")[-1]
            else:
                sku = json_info["sku"]
            name = sku + " - " + html.unescape(json_info["name"])

            if "REACONDICIONADO" in name.upper():
                condition = "https://schema.org/RefurbishedCondition"
            else:
                condition = "https://schema.org/NewCondition"

            key = soup.find("form", "product-form form-horizontal")["action"].split(
                "/"
            )[-1]

            if "PEDIDO" in name.upper():
                stock = 0
            else:
                stock = int(soup.find("input", {"id": "input-qty"})["max"])

            price = Decimal(json_info["offers"]["price"])
            picture_urls = []
            if "image" in json_info:
                picture_urls = [json_info["image"].split("?")[0]]
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
                part_number=sku,
                picture_urls=picture_urls,
                description=description,
                condition=condition,
            )
            return [p]
