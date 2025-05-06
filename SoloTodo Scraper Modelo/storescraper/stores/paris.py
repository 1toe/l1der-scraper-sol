import logging
import time
from collections import defaultdict
from decimal import Decimal
from bs4 import BeautifulSoup
import validators
from storescraper.categories import (
    ALL_IN_ONE,
    GAMING_CHAIR,
    TELEVISION,
    VACUUM_CLEANER,
    WATER_HEATER,
    STOVE,
    STEREO_SYSTEM,
    HEADPHONES,
    CELL,
    WEARABLE,
    TABLET,
    NOTEBOOK,
    VIDEO_GAME_CONSOLE,
    PRINTER,
    MONITOR,
    SOLID_STATE_DRIVE,
    PROJECTOR,
    MOUSE,
    KEYBOARD,
    COMPUTER_CASE,
    REFRIGERATOR,
    WASHING_MACHINE,
    DISH_WASHER,
    OVEN,
    SPACE_HEATER,
    SPLIT_AIR_CONDITIONER,
    ACCESORIES,
    PRINTER_SUPPLY,
    PERFUME,
    USB_FLASH_DRIVE,
    MEMORY_CARD,
    AIR_FRYER,
    BLENDER,
    COFFE_MAKER,
    COOKING_ROBOT,
    JUICER,
    KETTLE,
    ELECTRIC_GRILL,
    FOOD_PROCESSOR,
    SANDWICH_MAKER,
    ELECTRIC_POT,
    IRON,
    HAIR_CARE,
)
from storescraper.product import Product
from storescraper.store import Store
from storescraper.utils import html_to_markdown, session_with_proxy
from storescraper import banner_sections as bs


class Paris(Store):
    USER_AGENT = "solotodobot"
    RESULTS_PER_PAGE = 200

    category_paths = [
        ["tecnologia/computadores/ipad-tablet/", TABLET, 1],
        ["electro/audio/audifonos/", HEADPHONES, 1],
        ["electro/audio/parlantes-bluetooth-portables/", STEREO_SYSTEM, 1],
        ["electro/television/", TELEVISION, 1],
        ["electro/television/smart-tv/", TELEVISION, 1],
        ["electro/television/televisores-led/", TELEVISION, 1],
        ["television/televisores-oled-qled/", TELEVISION, 1],
        ["electro/television/soundbar-home-theater/", STEREO_SYSTEM, 1],
        ["electro/audio/", STEREO_SYSTEM, 0],
        ["electro/audio/micro-minicomponentes/", STEREO_SYSTEM, 1],
        ["electro/audio/audifonos-inalambricos/", HEADPHONES, 1],
        ["electro/audio-hifi/", STEREO_SYSTEM, 1],
        ["electro/audio-hifi/audifonos/", HEADPHONES, 1],
        ["electro/audio-hifi/home-theater/", STEREO_SYSTEM, 1],
        ["electro/audio-hifi/audio/", STEREO_SYSTEM, 1],
        ["electro/audio-hifi/parlantes/", STEREO_SYSTEM, 1],
        ["electro/elige-tu-pulgada/", TELEVISION, 1],
        ["electro/elige-tu-pulgada/30-a-39-pulgadas/", TELEVISION, 1],
        ["electro/elige-tu-pulgada/40-a-49-pulgadas/", TELEVISION, 1],
        ["electro/elige-tu-pulgada/50-a-59-pulgadas/", TELEVISION, 1],
        ["electro/elige-tu-pulgada/60-o-mas-pulgadas/", TELEVISION, 1],
        ["electro/elige-tu-pulgada/70-o-mas-pulgadas/", TELEVISION, 1],
        ["tecnologia/celulares/", CELL, 1],
        ["tecnologia/celulares/smartphone/", CELL, 1],
        ["tecnologia/celulares/iphone/", CELL, 1],
        ["tecnologia/celulares/samsung/", CELL, 1],
        ["tecnologia/celulares/xiaomi/", CELL, 1],
        ["tecnologia/celulares/motorola/", CELL, 1],
        ["tecnologia/celulares/honor/", CELL, 1],
        ["tecnologia/celulares/vivo/", CELL, 1],
        ["tecnologia/celulares/basicos/", CELL, 1],
        ["tecnologia/celulares/oppo/", CELL, 1],
        ["tecnologia/computadores/", NOTEBOOK, 0],
        ["tecnologia/computadores/desktop-all-in-one", ALL_IN_ONE, 1],
        ["tecnologia/computadores/notebooks/", NOTEBOOK, 1],
        ["tecnologia/computadores/ipad-tablet/", TABLET, 1],
        ["tecnologia/computadores/tablets-ninos/", TABLET, 1],
        ["tecnologia/computadores/apple/", NOTEBOOK, 1],
        ["tecnologia/wearables/", WEARABLE, 1],
        ["tecnologia/wearables/smartwatches/", WEARABLE, 1],
        ["tecnologia/wearables/smartwatches-ninos/", WEARABLE, 1],
        ["tecnologia/wearables/smartband/", WEARABLE, 1],
        ["tecnologia/consolas-videojuegos/", VIDEO_GAME_CONSOLE, 0],
        ["tecnologia/consolas-videojuegos/playstation-marca/", VIDEO_GAME_CONSOLE, 1],
        ["tecnologia/consolas-videojuegos/nintendo-marca/", VIDEO_GAME_CONSOLE, 1],
        ["tecnologia/consolas-videojuegos/xbox-marca/", VIDEO_GAME_CONSOLE, 1],
        ["tecnologia/impresoras/", PRINTER, 1],
        ["tecnologia/impresoras/laser/", PRINTER, 1],
        ["tecnologia/impresoras/tinta/", PRINTER, 1],
        ["tecnologia/impresoras/termicas-portatiles/", PRINTER, 1],
        ["tecnologia/impresoras/impresoras-3d/", PRINTER, 1],
        ["tecnologia/impresoras/impresion-industrial/", PRINTER, 1],
        ["tecnologia/impresoras/rotuladores/", PRINTER, 1],
        ["tecnologia/accesorios-computacion/", ACCESORIES, 1],
        ["tecnologia/accesorios-computacion/otros/", ACCESORIES, 1],
        ["tecnologia/accesorios-computacion/monitor-gamer/", MONITOR, 1],
        ["tecnologia/accesorios-computacion/disco-duro/", SOLID_STATE_DRIVE, 1],
        ["tecnologia/accesorios-computacion/proyectores/", PROJECTOR, 1],
        ["tecnologia/accesorios-computacion/mouse-teclados/", MOUSE, 1],
        ["tecnologia/accesorios-computacion/audifonos-microfonos/", HEADPHONES, 1],
        ["tecnologia/accesorios-computacion/pendrives/", USB_FLASH_DRIVE, 1],
        ["tecnologia/computadores/pc-gamer/", NOTEBOOK, 1],
        # ["tecnologia/gamer/teclados/", KEYBOARD, 1],
        # ["tecnologia/gamer/headset/", HEADPHONES, 1],
        # ["tecnologia/gamer/sillas-escritorios-gamer/", GAMING_CHAIR, 1],
        # ["tecnologia/gamer/gabinetes/", COMPUTER_CASE, 1],
        ["tecnologia/gamer/monitores/", MONITOR, 1],
        ["tecnologia/accesorios-fotografia/tarjetas-memoria/", MEMORY_CARD, 1],
        [
            "linea-blanca/electrodomesticos/?tipoProductoAll=Freidoras de Aire",
            AIR_FRYER,
            1,
        ],
        ["linea-blanca/electrodomesticos/batidoras-licuadoras/", BLENDER, 1],
        ["linea-blanca/electrodomesticos/cafeteras/", COFFE_MAKER, 1],
        ["linea-blanca/electrodomesticos/robot-cocina/", COOKING_ROBOT, 1],
        ["linea-blanca/electrodomesticos/sacajugos-exprimidores/", JUICER, 1],
        ["linea-blanca/electrodomesticos/hervidores/", KETTLE, 1],
        ["linea-blanca/electrodomesticos/parrillas-electricas/", ELECTRIC_GRILL, 1],
        ["linea-blanca/electrodomesticos/procesadores-picadoras/", FOOD_PROCESSOR, 1],
        ["linea-blanca/electrodomesticos/tostadores-sandwicheras/", SANDWICH_MAKER, 1],
        [
            "linea-blanca/electrodomesticos/arroceras-vaporeras-freidoras",
            ELECTRIC_POT,
            1,
        ],
        ["linea-blanca/electrodomesticos/otros-articulos/", ACCESORIES, 1],
        ["linea-blanca/cocina/campanas/", ACCESORIES, 1],
        ["linea-blanca/refrigeracion/", REFRIGERATOR, 1],
        ["linea-blanca/refrigeracion/freezer/", REFRIGERATOR, 1],
        [
            "linea-blanca/refrigeracion/refrigeradores/refrigerador-side-by-side/",
            REFRIGERATOR,
            1,
        ],
        ["linea-blanca/refrigeracion/refrigeradores/", REFRIGERATOR, 1],
        ["linea-blanca/refrigeracion/no-frost/", REFRIGERATOR, 1],
        ["linea-blanca/refrigeracion/frigobar-cavas/", REFRIGERATOR, 1],
        # ["linea-blanca/equipamiento-industrial/refrigeracion/", REFRIGERATOR, 1],
        ["linea-blanca/lavado-secado/", WASHING_MACHINE, 1],
        [
            "linea-blanca/lavado-secado/lavadoras-carga-frontal",
            WASHING_MACHINE,
            1,
        ],
        [
            "linea-blanca/lavado-secado/lavadoras-carga-superior",
            WASHING_MACHINE,
            1,
        ],
        ["linea-blanca/lavado-secado/todas/", WASHING_MACHINE, 1],
        ["linea-blanca/lavado-secado/lavadoras-secadoras/", WASHING_MACHINE, 1],
        ["linea-blanca/lavado-secado/secadoras-centrifugas/", WASHING_MACHINE, 1],
        ["linea-blanca/lavado-secado/lavavajillas/", DISH_WASHER, 1],
        ["linea-blanca/cocina/", STOVE, 0],
        ["linea-blanca/cocina/cocinas/", STOVE, 1],
        ["linea-blanca/cocina/encimeras/", STOVE, 1],
        ["linea-blanca/cocina/hornos-empotrables/", OVEN, 1],
        ["linea-blanca/cocina/kit-empotrables/", STOVE, 1],
        ["linea-blanca/electrodomesticos/microondas/", OVEN, 1],
        ["linea-blanca/electrodomesticos/hornos-electricos/", OVEN, 1],
        ["linea-blanca/estufas/", SPACE_HEATER, 1],
        ["linea-blanca/estufas/electricas/", SPACE_HEATER, 1],
        ["linea-blanca/estufas/parafina/", SPACE_HEATER, 1],
        ["linea-blanca/estufas/gas/", SPACE_HEATER, 1],
        ["linea-blanca/estufas/lena-pellets/", SPACE_HEATER, 1],
        ["linea-blanca/estufas/calefaccion-exterior/", SPACE_HEATER, 1],
        ["linea-blanca/estufas/calefones-termos/", WATER_HEATER, 1],
        ["linea-blanca/electrodomesticos/aspiradoras-enceradoras/", VACUUM_CLEANER, 1],
        ["linea-blanca/aspirado-limpieza/aspiradoras-arrastre/", VACUUM_CLEANER, 1],
        ["linea-blanca/aspirado-limpieza/aspiradoras-robot/", VACUUM_CLEANER, 1],
        ["linea-blanca/aspirado-limpieza/aspiradoras-verticales/", VACUUM_CLEANER, 1],
        ["linea-blanca/climatizacion/", SPLIT_AIR_CONDITIONER, 1],
        # [
        #    "linea-blanca/estufas/calefactores-split/",
        #    SPLIT_AIR_CONDITIONER,
        #    1,
        # ],
        [
            "linea-blanca/calefaccion/aire-acondicionado/",
            SPLIT_AIR_CONDITIONER,
            1,
        ],
        ["linea-blanca/climatizacion/ventilacion/", SPLIT_AIR_CONDITIONER, 1],
        ["linea-blanca/electrodomesticos/", ACCESORIES, 1],
        ["tecnologia/impresoras/insumos-accesorios/", PRINTER_SUPPLY, 1],
        ["belleza/perfumes/", PERFUME, 1],
        ["outlet/outlet-electro/outlet-televisores/", TELEVISION, 1],
        ["outlet/outlet-electro/outlet-audio/", HEADPHONES, 1],
        ["outlet/outlet-electro/outlet-hifi/", STEREO_SYSTEM, 1],
        ["outlet/outlet-linea-blanca/outlet-refrigeracion/", REFRIGERATOR, 1],
        # ["outlet/outlet-linea-blanca/outlet-lavadoras/", WASHING_MACHINE, 1],
        # ["outlet/outlet-linea-blanca/outlet-cocinas/", STOVE, 1],
        # ["outlet/outlet-linea-blanca/outlet-calefaccion/", SPACE_HEATER, 1],
        # ["outlet/outlet-linea-blanca/outlet-electrodomesticos/", ACCESORIES, 1],
        ["outlet/outlet-tecno/outlet-celulares/", CELL, 1],
        ["outlet/outlet-tecno/outlet-computadores/", NOTEBOOK, 1],
        ["outlet/outlet-tecno/outlet-ipads-y-tablets/", TABLET, 1],
        ["outlet/outlet-tecno/outlet-impresoras/", PRINTER_SUPPLY, 1],
        ["outlet/outlet-tecno/outlet-smartwatch/", WEARABLE, 1],
        ["linea-blanca/electrodomesticos/planchas/", IRON, 1],
        [
            "belleza/cuidado-capilar/?tipoProductoAll=Cepillos Alisadores,Alisadores de Pelo,Secadores de Pelo,Onduladores de Pelo",
            HAIR_CARE,
            1,
        ],
    ]

    @classmethod
    def categories(cls):
        cats = []
        for entry in cls.category_paths:
            cat = entry[1]
            if cat not in cats:
                cats.append(cat)

        return cats

    @classmethod
    def discover_entries_for_category(cls, category, extra_args=None):
        category_paths = cls.category_paths
        fast_mode = extra_args and extra_args.get("fast_mode", False)

        session = session_with_proxy(extra_args)
        product_entries = defaultdict(lambda: [])

        for e in category_paths:
            (category_path, local_category, weight) = e

            if local_category != category:
                continue

            base_url = "https://www.paris.cl/" + category_path
            logging.info("Obtaining base section data from " + base_url)
            retries = 0

            while retries < 2:
                response = session.get(base_url)

                if response.url == "https://www.paris.cl/404":
                    raise Exception("Invalid section: " + category_path)

                if "<h2>Estamos mejorando tu experiencia</h2>" in response.text:
                    retries += 1
                    time.sleep(30)
                else:
                    break

            soup = BeautifulSoup(response.text, "lxml")
            breadcrumbs_tag = soup.find("nav", {"aria-label": "breadcrumb"})

            if not breadcrumbs_tag:
                raise Exception(f"{base_url}, {response.status_code}, {response.text}")

            breadcrumbs = []

            for link_tag in breadcrumbs_tag.find_all("a"):
                breadcrumbs.append(link_tag.text.strip())

            breadcrumbs.append(soup.find("span", {"aria-current": "page"}).text.strip())
            section_name = " > ".join(breadcrumbs)
            category_group_id = soup.find("div", {"data-cnstrc-filter-value": True})[
                "data-cnstrc-filter-value"
            ]

            page = 1

            while True:
                if page > (15000 / cls.RESULTS_PER_PAGE):
                    raise Exception("Page overflow: " + category_path)

                payload = {
                    "filters": [
                        {"key": "group_id", "stringValues": [category_group_id]}
                    ],
                    "pagination": {"page": page, "pageSize": cls.RESULTS_PER_PAGE},
                    "sortBy": "relevance",
                    "serviceAbility": {
                        "sameDayDelivery": False,
                        "nextDayDelivery": False,
                        "storePickUp": False,
                    },
                    "sponsoredProducts": True,
                }

                if "tipoProductoAll=" in category_path:
                    payload["filters"].append(
                        {
                            "key": "tipoProductoAll",
                            "stringValues": category_path.split("?tipoProductoAll=")[
                                -1
                            ].split(","),
                        }
                    )

                if fast_mode:
                    payload["filters"].append(
                        {"key": "isMarketplace", "stringValues": ["false"]}
                    )

                response = session.post(
                    "https://be-paris-backend-cl-ms-api.ccom.paris.cl/products/",
                    json=payload,
                )

                json_response = response.json()
                containers_data = json_response["results"]

                if not containers_data:
                    break

                for idx, container in enumerate(containers_data):
                    product_url = (
                        f"https://www.paris.cl/{container['slug']['es-CL']}.html"
                    )

                    product_entries[product_url].append(
                        {
                            "category_weight": weight,
                            "section_name": section_name,
                            "value": cls.RESULTS_PER_PAGE * (page - 1) + idx + 1,
                        }
                    )

                page += 1

        if fast_mode:
            # Since the fast mode filters the results, it messes up the position data, so remove it altogether
            for url in product_entries.keys():
                product_entries[url] = []
        return product_entries

    @classmethod
    def discover_urls_for_keyword(cls, keyword, threshold, extra_args=None):
        session = session_with_proxy(extra_args)
        session.headers["User-Agent"] = cls.USER_AGENT
        product_urls = []

        page = 0

        while True:
            if page > 40:
                raise Exception("Page overflow")

            search_url = "https://www.paris.cl/search?q={}&sz={}&start={}".format(
                keyword, cls.RESULTS_PER_PAGE, page * cls.RESULTS_PER_PAGE
            )

            soup = BeautifulSoup(session.get(search_url).text, "lxml")
            containers = soup.findAll("li", "flex-item-products")

            if not containers:
                break

            for container in containers:
                product_url = container.find("a")["href"].split("?")[0]
                if "https" not in product_url:
                    product_url = "https://www.paris.cl" + product_url

                product_urls.append(product_url)

                if len(product_urls) == threshold:
                    return product_urls

            page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        session.headers["User-Agent"] = cls.USER_AGENT
        search_term = url.split("-")[-1].replace(".html", "")

        payload = {"term": search_term, "pagination": {"pageSize": 30}}
        response = session.post(
            "https://be-paris-backend-cl-ms-api.ccom.paris.cl/products/",
            json=payload,
        )

        json_response = response.json()

        if not json_response["results"]:
            return []

        if len(json_response["results"]) == 1:
            product_data = json_response["results"][0]
        else:
            for entry in json_response["results"]:
                if entry["key"] == url.split("-")[-1].replace(".html", ""):
                    product_data = entry
                    break

        name = f"{product_data['brand']} {product_data['name']['es-CL']}"

        sellers = product_data["sellers"]
        assert len(sellers) == 1
        seller = sellers[0] if sellers[0] != "Paris" else None
        master_variant = product_data["masterVariant"]
        sku = master_variant["sku"]
        normal_price_key = "offer" if "offer" in master_variant["prices"] else "regular"
        normal_price = Decimal(
            master_variant["prices"][normal_price_key]["value"]["centAmount"]
        )
        if "paymentMethod" in master_variant["prices"]:
            offer_price = Decimal(
                master_variant["prices"]["paymentMethod"]["value"]["centAmount"]
            )
            if offer_price > normal_price:
                offer_price = normal_price
        else:
            offer_price = normal_price

        picture_urls = [x["url"] for x in master_variant["images"]]
        cleaned_picture_urls = []

        for picture_url in picture_urls:
            if validators.url(picture_url):
                cleaned_picture_urls.append(picture_url)

        stock = 0 if seller else -1

        if "description" in product_data:
            description = html_to_markdown(product_data["description"]["es-CL"])
        else:
            description = ""

        for attribute in master_variant.get("attributes", []):
            description += f"\n{attribute['name']}: {str(attribute['value'])}"

        review_count = product_data.get("countRating", 0)
        if "averageRating" in product_data:
            review_avg_score = float(product_data["averageRating"])
        else:
            review_avg_score = None

        if "REACONDICIONADO" in name.upper():
            condition = "https://schema.org/RefurbishedCondition"
        else:
            condition = "https://schema.org/NewCondition"

        p = Product(
            name[:200],
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
            description=description,
            picture_urls=cleaned_picture_urls,
            review_count=review_count,
            review_avg_score=review_avg_score,
            seller=seller,
            condition=condition,
        )

        return [p]

    @classmethod
    def banners(cls, extra_args=None):
        base_url = "https://www.paris.cl/"
        session = session_with_proxy(extra_args)
        session.headers["User-Agent"] = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
        )
        banners = []

        res = session.get(base_url)
        soup = BeautifulSoup(res.text, "lxml")
        slide_containers = soup.find_all("div", "flex-none rounded-lg relative")

        for idx, banner_entry in enumerate(slide_containers):
            destination_url = banner_entry.find("a")
            picture_url = destination_url.find("source")["srcset"]

            banners.append(
                {
                    "url": base_url,
                    "picture_url": picture_url,
                    "destination_urls": [destination_url["href"]],
                    "key": picture_url,
                    "position": idx + 1,
                    "section": bs.HOME,
                    "subsection": bs.HOME,
                    "type": bs.SUBSECTION_TYPE_HOME,
                }
            )

        if not banners:
            raise Exception("No banners for Home section: " + base_url)

        return banners
