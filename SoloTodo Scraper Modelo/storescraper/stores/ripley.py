import logging
import re
import json
from datetime import datetime
from collections import defaultdict

import validators
from bs4 import BeautifulSoup
from decimal import Decimal

from storescraper.categories import (
    GAMING_CHAIR,
    NOTEBOOK,
    TABLET,
    USB_FLASH_DRIVE,
    EXTERNAL_STORAGE_DRIVE,
    ALL_IN_ONE,
    MONITOR,
    TELEVISION,
    REFRIGERATOR,
    STOVE,
    OVEN,
    DISH_WASHER,
    WASHING_MACHINE,
    CELL,
    STEREO_SYSTEM,
    OPTICAL_DISK_PLAYER,
    VIDEO_GAME_CONSOLE,
    SPLIT_AIR_CONDITIONER,
    SPACE_HEATER,
    WEARABLE,
    HEADPHONES,
    VACUUM_CLEANER,
    WATER_HEATER,
    ACCESORIES,
    ELECTRIC_GRILL,
    MOUSE,
    PRINTER_SUPPLY,
    PERFUME,
    IRON,
    HAIR_CARE,
)
from storescraper.store import Store
from storescraper.product import Product
from storescraper.flixmedia import flixmedia_video_urls
from storescraper.utils import (
    html_to_markdown,
    session_with_proxy,
    cf_session_with_proxy,
)
from storescraper import banner_sections as bs


class Ripley(Store):
    category_paths = [
        [
            "tecno/computacion/notebooks",
            [NOTEBOOK],
            "Tecno > Computación > Notebooks",
            1,
        ],
        [
            "tecno/computacion/notebooks-gamer",
            [NOTEBOOK],
            "Tecno > Computación > Notebooks gamer",
            1,
        ],
        [
            "tecno/computacion/tablets",
            [TABLET],
            "Tecno > Computación > Tablets",
            1,
        ],
        [
            "tecno/computacion/impresoras",
            [PRINTER_SUPPLY],
            "Tecno > Computación > Impresoras",
            1,
        ],
        [
            "tecno/computacion/almacenamiento",
            [USB_FLASH_DRIVE, EXTERNAL_STORAGE_DRIVE],
            "Tecno > Computación > Almacenamiento",
            0.5,
        ],
        [
            "tecno/computacion/pc-all-in-one",
            [ALL_IN_ONE],
            "Tecno > Computación > PC/All in one",
            1,
        ],
        [
            "tecno/computacion/monitores",
            [MONITOR],
            "Tecno > Computación > Monitores",
            1,
        ],
        # [
        #     "tecno/television/proyectores-smart",
        #     [PROJECTOR],
        #     "Tecno > Televisión > Proyectores smart",
        #     1,
        # ],
        [
            "tecno/computacion-gamer/monitores",
            [MONITOR],
            "Tecno > Computación Gamer > Monitores",
            1,
        ],
        ["tecno/television", [TELEVISION], "Tecno > Televisión", 1],
        ["tecno/television/smart-tv", [TELEVISION], "Tecno > Televisión > Smart TV", 1],
        [
            "tecno/television/ultra-hd-4k",
            [TELEVISION],
            "Tecno > Televisión > Ultra HD 4K",
            1,
        ],
        [
            "tecno/television/premium-tv-y-8k",
            [TELEVISION],
            "Tecno > Televisión > Premium y 8K",
            1,
        ],
        ["electro/refrigeracion", [REFRIGERATOR], "Electro > Refrigeración", 1],
        [
            "electro/refrigeracion/refrigerador-no-frost",
            [REFRIGERATOR],
            "Electro > Refrigeración > Refrigerador No Frost",
            1,
        ],
        [
            "electro/refrigeracion/side-by-side",
            [REFRIGERATOR],
            "Electro > Refrigeración > Side by Side",
            1,
        ],
        [
            "electro/refrigeracion/refrigeradores",
            [REFRIGERATOR],
            "Electro > Refrigeración > Refrigeradores",
            1,
        ],
        [
            "electro/refrigeracion/freezers-y-congeladores",
            [REFRIGERATOR],
            "Electro > Refrigeración > Freezers y congeladores",
            1,
        ],
        [
            "electro/refrigeracion/frigobar",
            [REFRIGERATOR],
            "Electro > Refrigeración > Frigobar",
            1,
        ],
        # ['electro/refrigeracion/door-in-door', [REFRIGERATOR],
        #  'Electro > Refrigeración > Door in Door', 1],
        ["electro/cocina/cocinas", [STOVE], "Electro > Cocina > Cocinas", 1],
        ["electro/cocina/encimeras", [STOVE], "Electro > Cocina > Encimeras", 1],
        [
            "electro/electrodomesticos/hornos-y-microondas",
            [OVEN],
            "Electro > Electrodomésticos > Hornos y Microondas",
            1,
        ],
        [
            "electro/cocina/lavavajillas",
            [DISH_WASHER],
            "Electro > Cocina > Lavavajillas",
            1,
        ],
        [
            "electro/aseo/robots-de-limpieza",
            [VACUUM_CLEANER],
            "Electro > Aseo > Aspiradoras de Arrastre",
            1,
        ],
        [
            "electro/aseo/aspiradoras-de-arrastre",
            [VACUUM_CLEANER],
            "Electro > Aseo > Aspiradoras de Arrastre",
            1,
        ],
        [
            "electro/aseo/aspiradoras-verticales",
            [VACUUM_CLEANER],
            "Electro > Aseo > Aspiradoras Verticales",
            1,
        ],
        ["electro/lavanderia", [WASHING_MACHINE], "Electro > Lavandería", 1],
        [
            "electro/lavanderia/lavadoras",
            [WASHING_MACHINE],
            "Electro > Lavandería > Lavadoras",
            1,
        ],
        [
            "electro/lavanderia/secadoras",
            [WASHING_MACHINE],
            "Electro > Lavandería > Secadoras",
            1,
        ],
        [
            "electro/lavanderia/lavadora-secadora",
            [WASHING_MACHINE],
            "Electro > Lavandería > Lavadora-secadora",
            1,
        ],
        # ['electro/lavanderia/doble-carga', [WASHING_MACHINE],
        #  'Electro > Lavandería > Doble carga', 1],
        [
            "tecno/celulares",
            [CELL],
            "Tecno > Celulares",
            1,
        ],
        ["tecno/audio-y-musica", [STEREO_SYSTEM], "Tecno > Audio y Música", 0],
        [
            "tecno/audio-y-musica/equipos-de-musica",
            [STEREO_SYSTEM],
            "Tecno > Audio y Música > Equipos de música",
            1,
        ],
        [
            "tecno/audio-y-musica/parlantes-bluetooth",
            [STEREO_SYSTEM],
            "Tecno > Audio y Música > Parlantes Portables",
            1,
        ],
        [
            "tecno/audio-y-musica/soundbar-y-home-theater",
            [STEREO_SYSTEM],
            "Tecno > Audio y Música > Soundbar y Home theater",
            1,
        ],
        [
            "tecno/television/bluray-dvd-y-tv-portatiles",
            [OPTICAL_DISK_PLAYER],
            "Tecno > Televisión > Bluray -DVD y TV Portátil",
            1,
        ],
        [
            "tecno/playstation/consolas",
            [VIDEO_GAME_CONSOLE],
            "Tecno > PlayStation > Consolas",
            1,
        ],
        [
            "tecno/nintendo/consolas",
            [VIDEO_GAME_CONSOLE],
            "Tecno > Nintendo > Consolas",
            1,
        ],
        # ['tecno/xbox/consolas', [VIDEO_GAME_CONSOLE],
        #  'Tecno > Xbox > Consolas', 1],
        [
            "electro/climatizacion/aire-acondicionado",
            [SPLIT_AIR_CONDITIONER],
            "Electro > Climatización > Ventiladores y aire acondicionado",
            1,
        ],
        [
            "electro/climatizacion/purificadores-y-humificadores",
            [SPLIT_AIR_CONDITIONER],
            "Electro > Climatización > Purificadores y humidificadores",
            1,
        ],
        [
            "electro/calefaccion",
            [SPACE_HEATER],
            "Electro > Climatización > Estufas y calefactores",
            1,
        ],
        [
            "tecno/smartwatches-y-smartbands",
            [WEARABLE],
            "Tecno > Telefonía > Smartwatches y Wearables > Garmin",
            1,
        ],
        [
            "tecno/audio-y-musica/audifonos",
            [HEADPHONES],
            "Tecno > Audio y Música > Audífonos",
            1,
        ],
        [
            "tecno/computacion-gamer/audifonos-gamer",
            [HEADPHONES],
            "Tecno > Computación Gamer > Audífonos Gamer",
            1,
        ],
        [
            "tecno/computacion-gamer/accesorios-gamer",
            [HEADPHONES],
            "Tecno > Computación Gamer > Accesorios Gamer",
            1,
        ],
        [
            "muebles/home-office-y-oficina/sillas-y-escritorios-gamer",
            [GAMING_CHAIR],
            "Tecno > Computación Gamer > Sillas Gamer",
            1,
        ],
        [
            "tecno/computacion-gamer/teclados-y-mouse-gamer",
            [MOUSE],
            "Tecno > Computación Gamer > Teclados y Mouse Gamer",
            1,
        ],
        [
            "ferreteria/cocina/calefont-y-termos",
            [WATER_HEATER],
            "Ferretería > Cocina > Calefont y Termos",
            1,
        ],
        [
            "electro/electrodomesticos",
            [ACCESORIES],
            "Electro > Electrodomésticos",
            1,
        ],
        [
            "electro/cocina/parrillas-electricas",
            [ELECTRIC_GRILL],
            "Electro > Cocina > Parrillas Eléctricas",
            1,
        ],
        [
            "tecno/smart-home/asistentes-virtuales",
            [STEREO_SYSTEM],
            "Tecno > Smart Home > Asistentes Virtuales",
            1,
        ],
        [
            "belleza/perfumeria?s=mdco",
            [PERFUME],
            "Belleza > Perfumería",
            1,
        ],
        [
            "electro/lavanderia/planchas-y-vaporizadores",
            [IRON],
            "Electro > Lavandería > Planchas y vaporizadores",
            1,
        ],
        [
            "electro/cuidado-personal/secadores-de-pelo",
            [HAIR_CARE],
            "Electro > Cuidado personal > Secadores de pelo",
            1,
        ],
        [
            "electro/cuidado-personal/alisadores",
            [HAIR_CARE],
            "Electro > Cuidado personal > Alisadores",
            1,
        ],
        [
            "electro/cuidado-personal/onduladores",
            [HAIR_CARE],
            "Electro > Cuidado personal > Onduladores",
            1,
        ],
    ]

    @classmethod
    def categories(cls):
        cats = set()

        for _, local_categories, _, _ in cls.category_paths:
            for local_category in local_categories:
                cats.add(local_category)

        return list(cats)

    @classmethod
    def discover_entries_for_category(cls, category, extra_args=None):
        category_paths = cls.category_paths
        session = cls.get_session(extra_args)
        fast_mode = extra_args and extra_args.get("fast_mode", False)
        product_entries = defaultdict(lambda: [])

        for e in category_paths:
            category_path, local_categories, section_name, category_weight = e

            if category not in local_categories:
                continue

            page = 1
            section_index = 1

            while True:
                if page > 1000:
                    raise Exception(f"Page overflow: {category_path}")

                separator = "&" if "?" in category_path else "?"
                url = f"https://simple.ripley.cl/api/v1/catalog-products/{category_path}{separator}page={page}"

                if fast_mode:
                    url += "&facet=Vendido%20por%3ARipley"

                print(url)

                http_response = session.post(url)
                try:
                    response = json.loads(http_response.text)
                except Exception:
                    if http_response.status_code == 404:
                        break
                    raise Exception(http_response.text)
                products = response["products"]

                assert products

                for product in products:
                    product_url = product["url"]

                    if product["partNumber"][:3] == "MPM":
                        continue

                    if fast_mode:
                        product_entries[product_url] = []
                    else:
                        product_entries[product_url].append(
                            {
                                "category_weight": category_weight,
                                "section_name": section_name,
                                "value": section_index,
                            }
                        )

                    section_index += 1

                if fast_mode and page >= 50:
                    break

                if (
                    response["pagination"]["actualPage"]
                    == response["pagination"]["totalPages"]
                ):

                    break

                page += 1

        return product_entries

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)

        session = cls.get_session(extra_args)
        response = session.get(url, allow_redirects=True, timeout=60).text
        soup = BeautifulSoup(response, "lxml")
        product_data = re.search(r"window.__PRELOADED_STATE__ = (.+);", response)

        if not product_data:
            return []

        product_json = json.loads(product_data.groups()[0])

        if "product" not in product_json:
            return None

        specs_json = product_json["product"]["product"]
        products = []

        for product_entry in specs_json["SKUs"]:
            sku = product_entry["partNumber"] + "P"
            url = specs_json["url"]
            name = specs_json["name"].strip()
            short_description = specs_json.get("shortDescription", "")

            # If it's a cell sold by Ripley directly (not Mercado Ripley) add the
            # "Prepago" information in its description
            if category in [CELL, "Unknown"] and "MPM" not in sku:
                name += " ({})".format(short_description)

            for attribute in product_entry["Attributes"]:
                if attribute["usage"] == "Defining":
                    name += " ({})".format(attribute["Values"][0]["values"])
                    break

            if "offerPrice" in product_entry["prices"]:
                normal_price = Decimal(product_entry["prices"]["offerPrice"]).quantize(
                    0
                )
            elif "listPrice" in product_entry["prices"]:
                normal_price = Decimal(product_entry["prices"]["listPrice"]).quantize(0)
            else:
                return []

            offer_price = Decimal(
                product_entry["prices"].get("cardPrice", normal_price)
            ).quantize(0)

            if offer_price > normal_price:
                offer_price = normal_price

            description = ""

            if "longDescription" in specs_json:
                description += html_to_markdown(specs_json["longDescription"])

            description += "\n\nAtributo | Valor\n-- | --\n"

            for attribute in specs_json["attributes"]:
                if "name" in attribute and "value" in attribute:
                    description += "{} | {}\n".format(
                        attribute["name"], attribute["value"]
                    )

            description += "\n\n"
            condition = "https://schema.org/NewCondition"

            if (
                "reacondicionado" in description.lower()
                or "reacondicionado" in name.lower()
                or "reacondicionado" in short_description.lower()
            ):
                condition = "https://schema.org/RefurbishedCondition"

            picture_urls = []

            for path in specs_json["images"]:
                picture_url = path

                if "file://" in picture_url:
                    continue

                if not picture_url.startswith("http"):
                    picture_url = "https:" + picture_url

                if not validators.url(picture_url):
                    continue

                picture_urls.append(picture_url)

            if not picture_urls:
                picture_urls = None

            if "shop_name" in specs_json["sellerOp"]:
                seller = specs_json["sellerOp"]["shop_name"]
            elif product_entry["isMarketplaceProduct"]:
                seller = "Mercado R"
            else:
                seller = None

            if seller == "Shop Ecsa":
                seller = None

            if seller:
                stock = 0
            elif product_entry["stock"]:
                stock = -1
            else:
                stock = 0

            flixmedia_id = None
            video_urls = []
            flixmedia_urls = [
                "//media.flixfacts.com/js/loader.js",
                "https://media.flixfacts.com/js/loader.js",
            ]

            for flixmedia_url in flixmedia_urls:
                flixmedia_tag = soup.find("script", {"src": flixmedia_url})

                if flixmedia_tag and flixmedia_tag.has_attr("data-flix-mpn"):
                    flixmedia_id = flixmedia_tag["data-flix-mpn"]
                    video_urls = flixmedia_video_urls(flixmedia_id)
                    break

            reviews_endpoint = (
                f"https://display.powerreviews.com/m/"
                "1243872956/l/all/product/{product.sku}/reviews?"
                "apikey=22c8538c-1cba-41bb-8d47-234a796148bf"
                "&_noconfig=true"
            )
            reviews_session = session_with_proxy(extra_args)
            reviews_response = reviews_session.get(reviews_endpoint).json()
            review_count = None
            review_avg_score = None

            if "results" in reviews_response:
                reviews_data = reviews_response["results"][0]

                if "rollup" in reviews_data:
                    review_count = reviews_data["rollup"]["rating_count"]
                    review_avg_score = reviews_data["rollup"]["average_rating"]
                else:
                    review_count = 0

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
                description=description,
                picture_urls=picture_urls,
                condition=condition,
                seller=seller,
                flixmedia_id=flixmedia_id,
                video_urls=video_urls,
                review_count=review_count,
                review_avg_score=review_avg_score,
            )
            products.append(p)

        return products

    @classmethod
    def discover_urls_for_keyword(cls, keyword, threshold, extra_args=None):
        session = cls.get_session(extra_args)
        session.headers["Content-Type"] = "application/json"

        filters = []

        if extra_args:
            if "brand_filter" in extra_args:
                filters.append(
                    {
                        "type": "brands",
                        "value": extra_args["brand_filter"],
                        "key": "brand.keyword",
                    }
                )

        product_urls = []
        page = 1

        while True:
            if page > 40:
                raise Exception("Page overflow")

            search_url = "https://simple.ripley.cl/api/v2/search"
            search_body = {
                "filters": filters,
                "term": keyword,
                "perpage": 24,
                "page": page,
                "sessionkey": "",
                "sort": "score",
            }
            session.post(search_url, json=search_body)
            response = session.post(search_url, json=search_body)
            search_results = json.loads(response.text)

            if "products" not in search_results:
                break

            for product in search_results["products"]:
                product_urls.append(product["url"])
                if len(product_urls) >= threshold:
                    return product_urls

            page += 1

        return product_urls

    @classmethod
    def banners(cls, extra_args=None):
        extra_args = cls._extra_args_with_preflight(extra_args)
        base_url = "https://simple.ripley.cl/{}"

        sections_data = [
            [bs.HOME, "Home", bs.SUBSECTION_TYPE_HOME, ""],
            [
                bs.ELECTRO_RIPLEY,
                "Electro Ripley",
                bs.SUBSECTION_TYPE_CATEGORY_PAGE,
                "electro",
            ],
            # [bs.TECNO_RIPLEY, 'Tecno Ripley',
            #  bs.SUBSECTION_TYPE_CATEGORY_PAGE, 'tecno'],
            [
                bs.REFRIGERATION,
                "Refrigeración",
                bs.SUBSECTION_TYPE_MOSAIC,
                "electro/refrigeracion/",
            ],
            [
                bs.REFRIGERATION,
                "Side by Side",
                bs.SUBSECTION_TYPE_MOSAIC,
                "electro/refrigeracion/side-by-side/",
            ],
            [
                bs.REFRIGERATION,
                "Refrigeradores",
                bs.SUBSECTION_TYPE_MOSAIC,
                "electro/refrigeracion/refrigeradores/",
            ],
            [
                bs.REFRIGERATION,
                "Freezers y congeladores",
                bs.SUBSECTION_TYPE_MOSAIC,
                "electro/refrigeracion/freezers-y-congeladores/",
            ],
            [
                bs.REFRIGERATION,
                "Door In Door",
                bs.SUBSECTION_TYPE_MOSAIC,
                "electro/refrigeracion/door-in-door/",
            ],
            [
                bs.REFRIGERATION,
                "Frigobar",
                bs.SUBSECTION_TYPE_MOSAIC,
                "electro/refrigeracion/frigobar/",
            ],
            [
                bs.REFRIGERATION,
                "Refrigeracion Comercial e Industrial",
                bs.SUBSECTION_TYPE_MOSAIC,
                "electro/refrigeracion/refrigeracion-comercial-e-industrial/",
            ],
            [
                bs.WASHING_MACHINES,
                "Lavandería",
                bs.SUBSECTION_TYPE_MOSAIC,
                "electro/lavanderia",
            ],
            [
                bs.WASHING_MACHINES,
                "Lavadoras",
                bs.SUBSECTION_TYPE_MOSAIC,
                "electro/lavanderia/lavadoras",
            ],
            [
                bs.WASHING_MACHINES,
                "Lavadora-secadora",
                bs.SUBSECTION_TYPE_MOSAIC,
                "electro/lavanderia/lavadora-secadora",
            ],
            [
                bs.WASHING_MACHINES,
                "Secadoras",
                bs.SUBSECTION_TYPE_MOSAIC,
                "electro/lavanderia/secadoras",
            ],
            [
                bs.WASHING_MACHINES,
                "Doble Carga",
                bs.SUBSECTION_TYPE_MOSAIC,
                "electro/lavanderia/doble-carga",
            ],
            [
                bs.TELEVISIONS,
                "Televisión",
                bs.SUBSECTION_TYPE_MOSAIC,
                "tecno/television",
            ],
            [
                bs.TELEVISIONS,
                "Smart TV",
                bs.SUBSECTION_TYPE_MOSAIC,
                "tecno/television/smart-tv",
            ],
            [
                bs.TELEVISIONS,
                "Ultra HD 4K",
                bs.SUBSECTION_TYPE_MOSAIC,
                "tecno/television/ultra-hd-4k",
            ],
            [
                bs.TELEVISIONS,
                "Premium y 8K",
                bs.SUBSECTION_TYPE_MOSAIC,
                "tecno/television/premium-tv-y-8k",
            ],
            [
                bs.AUDIO,
                "Audio y Música",
                bs.SUBSECTION_TYPE_MOSAIC,
                "tecno/audio-y-musica",
            ],
            [
                bs.AUDIO,
                "Parlantes Portables",
                bs.SUBSECTION_TYPE_MOSAIC,
                "tecno/audio-y-musica/parlantes-bluetooth",
            ],
            [
                bs.AUDIO,
                "Soundbar y Home theater",
                bs.SUBSECTION_TYPE_MOSAIC,
                "tecno/audio-y-musica/soundbar-y-home-theater",
            ],
            [
                bs.AUDIO,
                "Receiver y Amplificadores",
                bs.SUBSECTION_TYPE_MOSAIC,
                "tecno/audio-y-musica/receiver-y-amplificadores",
            ],
            [
                bs.AUDIO,
                "Equipos de música",
                bs.SUBSECTION_TYPE_MOSAIC,
                "tecno/audio-y-musica/equipos-de-musica",
            ],
            [
                bs.AUDIO,
                "Accesorios",
                bs.SUBSECTION_TYPE_MOSAIC,
                "tecno/audio-y-musica/accesorios-audio",
            ],
            [bs.CELLS, "Telefonía", bs.SUBSECTION_TYPE_MOSAIC, "tecno/celulares"],
            [bs.CELLS, "iPhone", bs.SUBSECTION_TYPE_MOSAIC, "tecno/celulares/iphone"],
        ]

        banners = []

        for section, subsection, subsection_type, url_suffix in sections_data:
            url = base_url.format(url_suffix)
            print(url)

            if subsection_type == bs.SUBSECTION_TYPE_HOME:
                banners = banners + cls.get_owl_banners(
                    url, section, subsection, subsection_type, extra_args
                )

            elif subsection_type == bs.SUBSECTION_TYPE_CATEGORY_PAGE:
                banners = banners + cls.get_owl_banners(
                    url, section, subsection, subsection_type, extra_args
                )
            elif subsection_type == bs.SUBSECTION_TYPE_MOSAIC:
                session = cls.get_session(extra_args)

                response = session.get(url)
                soup = BeautifulSoup(response.text, "lxml")

                if soup.find("svg", {"title": "nofound"}):
                    logging.warning("Deactivated category: " + url)
                    continue

                banners_container = soup.find("section", "catalog-top-banner")

                if not banners_container:
                    print("No banners for: " + url)
                    continue

                idx = 1
                for banner_link in banners_container.findAll("a"):
                    if "item" in banner_link.attrs.get("class", []):
                        continue
                    picture_url = banner_link.find("img")

                    if not picture_url:
                        continue

                    banners.append(
                        {
                            "url": url,
                            "picture_url": picture_url.get("src")
                            or picture_url.get("data-src"),
                            "destination_urls": [banner_link["href"]],
                            "key": picture_url.get("src")
                            or picture_url.get("data-src"),
                            "position": idx,
                            "section": section,
                            "subsection": subsection,
                            "type": subsection_type,
                        }
                    )
                    idx += 1
            else:
                raise Exception("Invalid subsection type")

        return banners

    @classmethod
    def get_owl_banners(cls, url, section, subsection, subsection_type, extra_args):
        session = cls.get_session(extra_args)
        banners = []

        if subsection_type == bs.SUBSECTION_TYPE_HOME:
            response = session.get(
                "https://simple.ripley.cl/marketingcomponent/api/bff/marketing"
            )
            response = response.json()

            for response_section in response:
                if (
                    response_section["type"] == "zone_a"
                    and response_section["data"][0]["sliceType"] == "homebanner"
                ):
                    banner_items = response_section["data"][0]["items"]
                    break
            else:
                raise Exception("No banner items for Home section")

            for idx, banner in enumerate(banner_items):
                picture_url = banner["image"]["originalURL"].split("?")[0]
                banners.append(
                    {
                        "url": url,
                        "picture_url": picture_url,
                        "destination_urls": [banner["url"]["url"]],
                        "key": picture_url,
                        "position": idx + 1,
                        "section": section,
                        "subsection": subsection,
                        "type": subsection_type,
                    }
                )

            if not banners:
                raise Exception("No banners for Home section: " + url)

        else:
            response = session.get(url + "?v=2")
            soup = BeautifulSoup(response.text, "lxml")
            carousel_tag = soup.find("div", "home-carousel")

            if carousel_tag:
                carousel_tag = carousel_tag.find("div")
                for idx, banner_tag in enumerate(carousel_tag.findAll(recursive=False)):
                    if banner_tag.name == "a":
                        destination_urls = [banner_tag["href"]]
                        if banner_tag.find("img"):
                            picture_url = banner_tag.find("img")["src"]
                        else:
                            picture_style = banner_tag.find("span")["style"]
                            picture_url = re.search(
                                r"url\((.+)\)", picture_style
                            ).groups()[0]

                        banners.append(
                            {
                                "url": url,
                                "picture_url": picture_url,
                                "destination_urls": destination_urls,
                                "key": picture_url,
                                "position": idx + 1,
                                "section": section,
                                "subsection": subsection,
                                "type": subsection_type,
                            }
                        )
                    else:
                        # Collage
                        desktop_container_tag = banner_tag.find("div")
                        cell_tags = desktop_container_tag.findAll("a")
                        destination_urls = [
                            tag["href"] for tag in cell_tags if "href" in tag.attrs
                        ]
                        picture_url = desktop_container_tag.find("img")["src"]

                        banners.append(
                            {
                                "url": url,
                                "picture_url": picture_url,
                                "destination_urls": destination_urls,
                                "key": picture_url,
                                "position": idx + 1,
                                "section": section,
                                "subsection": subsection,
                                "type": subsection_type,
                            }
                        )
            else:
                carousel_tag = soup.find("ul", "splide__list")
                if carousel_tag:
                    for idx, banner_tag in enumerate(carousel_tag.findAll("li")):
                        banner_link = banner_tag.find("a")
                        destination_urls = [banner_link["href"]]
                        picture_url = banner_link.find("img")["src"]

                        banners.append(
                            {
                                "url": url,
                                "picture_url": picture_url,
                                "destination_urls": destination_urls,
                                "key": picture_url,
                                "position": idx + 1,
                                "section": section,
                                "subsection": subsection,
                                "type": subsection_type,
                            }
                        )

        if not banners:
            print("No banners for: " + url)

        return banners

    @classmethod
    def reviews_for_sku(cls, sku):
        print(sku)
        session = session_with_proxy(None)
        reviews = []
        page = 1

        while True:
            print(page)
            reviews_endpoint = (
                "https://display.powerreviews.com/m/303286/l/"
                "es_ES/product/{}/reviews?"
                "apikey=71f6caaa-ea4f-43b9-a19e-46eccb73bcbb"
                "&paging.size=25&paging.from={}".format(sku, page)
            )
            response = session.get(reviews_endpoint).json()

            if response["paging"]["current_page_number"] != page:
                break

            for entry in response["results"][0]["reviews"]:
                review_date = datetime.fromtimestamp(
                    entry["details"]["created_date"] / 1000
                )

                review = {
                    "store": "Ripley",
                    "sku": sku,
                    "rating": float(entry["metrics"]["rating"]),
                    "text": entry["details"]["comments"],
                    "date": review_date.isoformat(),
                }

                reviews.append(review)

            page += 1

        return reviews

    @classmethod
    def get_session(cls, extra_args=None):
        return cf_session_with_proxy(extra_args)
