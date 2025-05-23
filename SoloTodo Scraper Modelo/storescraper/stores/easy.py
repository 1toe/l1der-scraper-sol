import json
import re
from collections import defaultdict
from decimal import Decimal
from bs4 import BeautifulSoup

from storescraper import banner_sections as bs

from storescraper.categories import (
    SPLIT_AIR_CONDITIONER,
    OVEN,
    REFRIGERATOR,
    SPACE_HEATER,
    VACUUM_CLEANER,
    WASHING_MACHINE,
    VIDEO_GAME_CONSOLE,
    WATER_HEATER,
    STOVE,
    ACCESORIES,
)

from storescraper.product import Product
from storescraper.store import Store
from storescraper.utils import session_with_proxy, html_to_markdown


class Easy(Store):
    base_url = "https://cl-ccom-easy-bff-web.ecomm.cencosud.com/v2"

    @classmethod
    def categories(cls):
        return [
            REFRIGERATOR,
            OVEN,
            VACUUM_CLEANER,
            WASHING_MACHINE,
            SPLIT_AIR_CONDITIONER,
            SPACE_HEATER,
            VIDEO_GAME_CONSOLE,
            WATER_HEATER,
            STOVE,
        ]

    @classmethod
    def discover_entries_for_category(cls, category, extra_args=None):
        category_paths = [
            # Electrohogar y climatización
            # Calefacción
            [
                "electrohogar-y-climatizacion/calefaccion/estufas-electricas",
                [SPACE_HEATER],
                "Inicio > Electrohogar > Calefacción > Estufas Eléctricas",
                1,
            ],
            [
                "electrohogar-y-climatizacion/calefaccion/estufas-a-pellet",
                [SPACE_HEATER],
                "Inicio > Electrohogar > Calefacción > Estufas a Pellet",
                1,
            ],
            [
                "electrohogar-y-climatizacion/calefaccion/estufas-a-gas",
                [SPACE_HEATER],
                "Inicio > Electrohogar > Calefacción > Estufas a Gas",
                1,
            ],
            [
                "electrohogar-y-climatizacion/calefaccion/estufas-a-parafina",
                [SPACE_HEATER],
                "Inicio > Electrohogar > Calefacción > Estufas a Parafina",
                1,
            ],
            [
                "electrohogar-y-climatizacion/calefaccion/estufas-a-lena",
                [SPACE_HEATER],
                "Inicio > Electrohogar > Calefacción > Estufas a leña",
                1,
            ],
            # Refrigeración
            [
                "electrohogar-y-climatizacion/refrigeracion/refrigeradores",
                [REFRIGERATOR],
                "Inicio > Electrohogar y Climatización > Refrigeración > "
                "Refrigeradores",
                1,
            ],
            [
                "electrohogar-y-climatizacion/refrigeracion/freezer",
                [REFRIGERATOR],
                "Inicio > Electrohogar y Climatización > Refrigeración > " "Freezer",
                1,
            ],
            [
                "electrohogar-y-climatizacion/refrigeracion/frigobar",
                [REFRIGERATOR],
                "Inicio > Electrohogar y Climatización > Refrigeración > " "Frigobar",
                1,
            ],
            # Cocina
            [
                "electrohogar-y-climatizacion/cocina/hornos-empotrables",
                [OVEN],
                "Inicio > Electrohogar y Climatización > Cocina > "
                "Hornos Empotrables",
                1,
            ],
            [
                "electrohogar-y-climatizacion/electrodomesticos/microondas",
                [OVEN],
                "Inicio > Electrohogar y Climatización > Cocina > Microondas",
                1,
            ],
            # Lavado y planchado
            [
                "electrohogar-y-climatizacion/lavado-y-planchado/lavadoras",
                [WASHING_MACHINE],
                "Inicio > Electrohogar y Climatización > Lavado y planchado > "
                "Lavadoras",
                1,
            ],
            [
                "electrohogar-y-climatizacion/lavado-y-planchado/secadoras",
                [WASHING_MACHINE],
                "Inicio > Electrohogar y Climatización > Lavado y planchado > "
                "Secadoras",
                1,
            ],
            [
                "electrohogar-y-climatizacion/lavado-y-planchado/lavadoras-"
                "secadoras",
                [WASHING_MACHINE],
                "Inicio > Electrohogar y Climatización > Lavado y planchado > "
                "Lava - seca",
                1,
            ],
            # Aspirado y limpieza
            [
                "electrohogar-y-climatizacion/aspirado-y-limpieza/aspiradoras",
                [VACUUM_CLEANER],
                "Inicio > Electrohogar y Climatización > Aspirado y limpieza > "
                "Aspiradoras",
                1,
            ],
            [
                "electrohogar-y-climatizacion/aspirado-y-limpieza/robots-de-"
                "limpieza",
                [VACUUM_CLEANER],
                "Inicio > Electrohogar y Climatización > Aspirado y limpieza > "
                "Robots de limpieza",
                1,
            ],
            # Electrodomésticos
            [
                "electrohogar-y-climatizacion/electrodomesticos/hornos-" "electricos",
                [OVEN],
                "Inicio > Electrohogar y Climatización > Electrodomésticos > "
                "Hornos eléctricos",
                1,
            ],
            [
                "electrohogar-y-climatizacion/electrodomesticos/microondas",
                [OVEN],
                "Inicio > Electrohogar y Climatización > Electrodomésticos > "
                "Microondas",
                1,
            ],
            # Ventilación
            [
                "electrohogar-y-climatizacion/ventilacion/aire-acondicionado-"
                "portatil",
                [SPLIT_AIR_CONDITIONER],
                "Inicio > Electrohogar y Climatización > Ventilación > "
                "Aire acondicionado portátil",
                1,
            ],
            [
                "electrohogar-y-climatizacion/ventilacion/aire-acondicionado-" "split",
                [SPLIT_AIR_CONDITIONER],
                "Inicio > Electrohogar y Climatización > Ventilación > "
                "Aire Acondicionado split",
                1,
            ],
            [
                "electrohogar-y-climatizacion/ventilacion/purificadores-y-"
                "humidificadores",
                [SPLIT_AIR_CONDITIONER],
                "Inicio > Electrohogar y Climatización > Ventilación > "
                "Purificadores y humidificadores",
                1,
            ],
            [
                "electrohogar-y-climatizacion/calefont-y-termos/calefont",
                [WATER_HEATER],
                "Inicio > Electrohogar y Climatización > Calefont y Termos > "
                "Calefont",
                1,
            ],
            [
                "electrohogar-y-climatizacion/tecnologia/consolas-y-"
                "videojuegos/consolas",
                [VIDEO_GAME_CONSOLE],
                "Electrohogar y Climatización > Tecnología > "
                "Consolas y Videojuegos > Consolas",
                1,
            ],
            [
                "electrohogar-y-climatizacion/cocina/cocinas-a-gas",
                [STOVE],
                "Electrohogar y Climatización > Cocina > Cocina a gas",
                1,
            ],
            [
                "electrohogar-y-climatizacion/cocina/encimeras",
                [STOVE],
                "Electrohogar y Climatización > Cocina > Encimeras",
                1,
            ],
            [
                "electrohogar-y-climatizacion/electrodomesticos",
                [ACCESORIES],
                "Electrohogar y Climatización > Electrodomésticos",
                1,
            ],
        ]

        product_entries = defaultdict(lambda: [])
        session = session_with_proxy(extra_args)

        for e in category_paths:
            category_path, local_categories, section_name, category_weight = e

            if category not in local_categories:
                continue

            page = 1

            while True:
                if page > 20:
                    raise Exception("page overflow: " + category_path)

                url = f"{cls.base_url}/search/categories?count=40&page={page}&categories={category_path}"

                response = session.get(
                    url, headers={"X-Api-Key": "jFt3XhoLqFAGr6qN9SCpr9K6y83HpakP"}
                ).json()

                if response["productList"] == []:
                    break

                for idx, product in enumerate(response["productList"]):
                    product_entries[
                        f"https://www.easy.cl/{product['linkText']}/p"
                    ].append(
                        {
                            "category_weight": category_weight,
                            "section_name": section_name,
                            "value": idx + 1,
                        }
                    )

                page += 1

        return product_entries

    @classmethod
    def discover_urls_for_keyword(cls, keyword, threshold, extra_args=None):
        session = session_with_proxy(extra_args)
        product_urls = []
        page = 1

        while True:
            response = session.get(
                f"{cls.base_url}/search?count=40&page={page}&query={keyword}",
                headers={"X-Api-Key": "jFt3XhoLqFAGr6qN9SCpr9K6y83HpakP"},
            ).json()

            if response["productList"] == []:
                break

            for product in response["productList"]:
                product_urls.append(f"https://www.easy.cl/{product['linkText']}/p")

                if len(product_urls) == threshold:
                    return product_urls

            page += 1

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        item_id = re.findall(r"-(\d+)", url)[-1]
        response = session.get(
            f"{cls.base_url}/products/by-sku/{item_id}",
            headers={"X-Api-Key": "jFt3XhoLqFAGr6qN9SCpr9K6y83HpakP"},
        )

        if response.status_code == 404:
            return []

        response = response.json()
        assert response["items"]

        description = html_to_markdown(response["description"])
        description += "\n"

        specs_keys_blacklist = response.get("allSpecificationsGroups", [])
        for local_key, value in response.get("specifications", {}).items():
            if local_key in specs_keys_blacklist:
                continue
            description += f"{local_key}: {', '.join([str(x) for x in value])}\n"

        products = []
        for item in response["items"]:
            if "images" not in item:
                continue

            assert len(item["referenceId"]) == 1
            assert item["referenceId"][0]["Key"] == "RefId"
            sku = item["referenceId"][0]["Value"]

            if "itemSpecifications" in item:
                variations_axis = item["itemSpecifications"]["variations"]
                variations_entries = " / ".join(
                    [item["itemSpecifications"][axis][0] for axis in variations_axis]
                )
                name = f"{response['brand']} {item['name']} ({variations_entries})"
            else:
                name = f"{response['brand']} {item['name']}"

            picture_urls = [img["imageUrl"] for img in item["images"]]

            for seller in item["sellers"]:
                if seller["sellerName"] == "Easy.cl":
                    offer = seller["commertialOffer"]

                    if (
                        "offerPrice" in offer["prices"]
                        and offer["prices"]["offerPrice"]
                    ):
                        normal_price = Decimal(offer["prices"]["offerPrice"])
                    else:
                        normal_price = Decimal(offer["prices"]["normalPrice"])

                    if (
                        "brandPrice" in offer["prices"]
                        and offer["prices"]["brandPrice"]
                    ):
                        offer_price = Decimal(offer["prices"]["brandPrice"])
                    else:
                        offer_price = normal_price

                    stock = offer["availableQuantity"]
                    break
            else:
                continue

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
                picture_urls=picture_urls,
                description=description,
            )
            products.append(p)

        return products

    @classmethod
    def banners(cls, extra_args=None):
        base_url = "https://www.easy.cl"
        session = session_with_proxy(extra_args)
        soup = BeautifulSoup(session.get(base_url).text, "lxml")
        build_id = json.loads(soup.find("script", {"id": "__NEXT_DATA__"}).text)[
            "buildId"
        ]
        response = session.get(f"{base_url}/_next/data/{build_id}/index.json").json()
        content_data = response["pageProps"]["repo"]["content"]
        banners_data = None

        for content in content_data:
            if content["component"] == "banner-carousel":
                banners_data = content
                break

        banners = []

        for idx, banner in enumerate(banners_data["items"]):
            banner_link = banner["link"]
            banner_url = (
                f"{base_url}{banner_link}"
                if banner_link[0] == "/"
                else f"{base_url}/{banner_link}"
            )

            banners.append(
                {
                    "url": base_url,
                    "picture_url": banner["image"],
                    "destination_urls": [banner_url],
                    "key": banner["image"],
                    "position": idx + 1,
                    "section": bs.HOME,
                    "subsection": bs.HOME,
                    "type": bs.SUBSECTION_TYPE_HOME,
                }
            )

        if not banners:
            raise Exception(f"No banners for Home section: {base_url}")

        return banners
