import json
import validators
from decimal import Decimal
from pathlib import Path
from storescraper.categories import (
    SPLIT_AIR_CONDITIONER,
    ALL_IN_ONE,
    CELL,
    DISH_WASHER,
    EXTERNAL_STORAGE_DRIVE,
    GAMING_CHAIR,
    KEYBOARD,
    ACCESORIES,
    MEMORY_CARD,
    MONITOR,
    NOTEBOOK,
    MOUSE,
    HEADPHONES,
    OVEN,
    PRINTER,
    PROJECTOR,
    REFRIGERATOR,
    SOLID_STATE_DRIVE,
    SPACE_HEATER,
    STEREO_SYSTEM,
    TABLET,
    TELEVISION,
    USB_FLASH_DRIVE,
    VACUUM_CLEANER,
    VIDEO_GAME_CONSOLE,
    WASHING_MACHINE,
    WEARABLE,
    PRINTER_SUPPLY,
    IRON,
    HAIR_CARE,
)
from storescraper.product import Product
from storescraper.store import Store
from storescraper.utils import (
    html_to_markdown,
    session_with_proxy,
    cf_session_with_proxy,
)
from storescraper import banner_sections as bs


class Lider(Store):
    preferred_discover_urls_concurrency = 3
    preferred_products_for_url_concurrency = 3
    USER_AGENTS = [
        "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
        "Mozilla/5.0 (X11; Debian; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:115.0) Gecko/20100101 Firefox/115.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0",
        "Mozilla/5.0 (X11; Arch Linux; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
        "Mozilla/5.0 (Linux; Android 13; Redmi Note 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.135 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 11; Pixel 4a) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.135 Mobile Safari/537.36 EdgA/131.0.2903.87",
        "Mozilla/5.0 (Linux; Android 12; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/24.0 Chrome/131.0.6778.135 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 13; SAMSUNG SM-G990B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/24.0 Chrome/123.0.6312.105 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 12; 220733SG Build/SP1A.210812.016) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.135 Mobile Safari/537.3",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 16_4 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.2420.65",
    ]

    tenant = "catalogo"
    category_paths = [
        # TECNO
        ["66849718_44699651_73841472", [TELEVISION], "Tecno > TV", 1],
        # ["Tecno/TV/Smart_TV", [TELEVISION], "Tecno > TV > Smart TV", 1],
        # [
        #     "Tecno/TV/Smart_TV_Hasta_50_Pulgadas",
        #     [TELEVISION],
        #     "Tecno > TV > Smart TV Hasta 50 Pulgadas",
        #     1,
        # ],
        # [
        #     "Tecno/TV/Smart_TV_Sobre_50_Pulgadas",
        #     [TELEVISION],
        #     "Tecno > TV > Smart TV Sobre 50 Pulgadas",
        #     1,
        # ],
        ["66849718_44699651_64332442", [STEREO_SYSTEM], "Tecno > TV > Home Theater", 1],
        ["66849718_44699651_68838150", [PROJECTOR], "Tecno > TV > Proyectores", 1],
        ["66849718_14621386", [STEREO_SYSTEM], "Tecno > Audio", 1],
        [
            "66849718_14621386_88231649",
            [STEREO_SYSTEM],
            "Tecno > Audio > Equipos de Música y Karaoke",
            1,
        ],
        [
            "66849718_14621386_95114916",
            [STEREO_SYSTEM],
            "Tecno > Audio > Equipos de Música y Karaoke",
            1,
        ],
        [
            "66849718_14621386_49644492",
            [STEREO_SYSTEM],
            "Tecno > Audio > Audio Portable",
            1,
        ],
        [
            "66849718_14621386_25354977",
            [STEREO_SYSTEM],
            "Tecno > Audio > Micro y Mini Componentes",
            1,
        ],
        ["66849718_14621386_31940338", [HEADPHONES], "Tecno > Audio > Audífonos", 1],
        [
            "66849718_14621386_27642866",
            [STEREO_SYSTEM],
            "Tecno > Audio > Tornamesas y Vinilos",
            1,
        ],
        [
            "66849718_14621386_98336174",
            [STEREO_SYSTEM],
            "Tecno > Audio > Audio HI-FI",
            1,
        ],
        [
            "66849718_44699651_68838150",
            [PROJECTOR],
            "Tecno > TV > Proyectores",
            1,
        ],
        [
            "66849718_80980590_45869788",
            [VIDEO_GAME_CONSOLE],
            "Tecno > Videojuegos > Consolas",
            1,
        ],
        [
            "66849718_80980590_97449970",
            [VIDEO_GAME_CONSOLE],
            "Tecno > Videojuegos > Nintendo",
            1,
        ],
        [
            "66849718_80980590_45368401",
            [VIDEO_GAME_CONSOLE],
            "Tecno > Videojuegos > PlayStation",
            1,
        ],
        [
            "66849718_80980590_47691134",
            [VIDEO_GAME_CONSOLE],
            "Tecno > Videojuegos > XBOX",
            1,
        ],
        # CELULARES
        ["34388900_60412644", [CELL], "Celulares > Celulares y Teléfonos", 1],
        [
            "34388900_13662451",
            [WEARABLE],
            "Celulares > Smartwatches y Wearables",
            1,
        ],
        # COMPUTACION
        [
            "89057520_72573679_94067303",
            [NOTEBOOK],
            "Computación > Computadores > Notebooks",
            1,
        ],
        [
            "89057520_72573679_62826909",
            [TABLET],
            "Computación > Computadores > Tablets",
            1,
        ],
        [
            "89057520_72573679_56612565",
            [ALL_IN_ONE],
            "Computación > Computadores > Computadores All in One",
            1,
        ],
        [
            "89057520_28386364_21832538",
            [MONITOR],
            "Computación > Accesorios Computación > Monitores y Proyectores",
            1.0,
        ],
        [
            "89057520_28386364",
            [MOUSE],
            "Computación > Computadores > Accesorios Computación",
            1.0,
        ],
        [
            "89057520_92341690_33654871",
            [NOTEBOOK],
            "Computación > Mundo Gamer > Computación Gamer",
            1.0,
        ],
        [
            "89057520_92341690_99170494",
            [KEYBOARD],
            "Computación > Mundo Gamer > Mouse y Teclados",
            1.0,
        ],
        [
            "89057520_92341690_27961626",
            [HEADPHONES],
            "Computación > Mundo Gamer > Audífonos",
            1.0,
        ],
        [
            "89057520_92341690_04804406",
            [GAMING_CHAIR],
            "Computación > Mundo Gamer > Sillas Gamer",
            1,
        ],
        [
            "89057520_18938454_77669169",
            [PRINTER],
            "Computación > Impresión > Impresoras y Multifuncionales",
            1.0,
        ],
        [
            "89057520_98848773_69232935",
            [EXTERNAL_STORAGE_DRIVE],
            "Computación > Almacenamiento > Discos Duros",
            1.0,
        ],
        [
            "89057520_98848773_37896447",
            [SOLID_STATE_DRIVE],
            "Computación > Almacenamiento > Discos Duros SSD",
            1.0,
        ],
        [
            "89057520_98848773_32568051",
            [MEMORY_CARD],
            "Computación > Almacenamiento > Tarjetas de Memoria",
            1.0,
        ],
        [
            "89057520_98848773_93306813",
            [USB_FLASH_DRIVE],
            "Computación > Almacenamiento > Pendrives",
            1.0,
        ],
        # ELECTROHOGAR
        [
            "23989399_93795889",
            [REFRIGERATOR],
            "Electrohogar > Refrigeración",
            1.0,
        ],
        [
            "23989399_93795889_28605677",
            [REFRIGERATOR],
            "Electrohogar > Refrigeración > No Frost",
            1.0,
        ],
        [
            "23989399_93795889_24472802",
            [REFRIGERATOR],
            "Electrohogar > Refrigeración > Frio Directo",
            1.0,
        ],
        [
            "23989399_93795889_98442409",
            [REFRIGERATOR],
            "Electrohogar > Refrigeración > Side By Side",
            1.0,
        ],
        [
            "23989399_93795889_83823051",
            [REFRIGERATOR],
            "Electrohogar > Refrigeración > Freezer",
            1.0,
        ],
        [
            "23989399_93795889_10449779",
            [REFRIGERATOR],
            "Electrohogar > Refrigeración > Frigobar",
            1.0,
        ],
        [
            "23989399_75788044",
            [WASHING_MACHINE],
            "Electrohogar > Lavado y Planchado",
            1.0,
        ],
        [
            "23989399_75788044_27277508",
            [WASHING_MACHINE],
            "Electrohogar > Lavado y Planchado > Lavadoras",
            1.0,
        ],
        [
            "23989399_75788044_75760841",
            [WASHING_MACHINE],
            "Electrohogar > Lavado y Planchado > Lavadoras Secadoras",
            1.0,
        ],
        [
            "23989399_75788044_83679483",
            [WASHING_MACHINE],
            "Electrohogar > Lavado y Planchado > Secadoras",
            1.0,
        ],
        [
            "23989399_75788044_84624586",
            [DISH_WASHER],
            "Electrohogar > Lavado y Planchado > Lavavajillas",
            1.0,
        ],
        [
            "23989399_85011192",
            [VACUUM_CLEANER],
            "Electrohogar > Aspiradoras y Limpieza",
            1.0,
        ],
        [
            "23989399_53512871_73118366",
            [OVEN],
            "Electrohogar > Electrodomésticos Cocina > Hornos Eléctricos",
            1.0,
        ],
        [
            "23989399_53512871_12048011",
            [OVEN],
            "Electrohogar > Electrodomésticos Cocina > Microondas",
            1.0,
        ],
        [
            "23989399_74640407_68912278",
            [OVEN],
            "Electrohogar > Cocinas > Hornos Empotrables",
            1.0,
        ],
        # [
        #     "Climatización/Calefacción",
        #     [SPACE_HEATER],
        #     "Electrohogar > Climatización > Calefacción",
        #     1.0,
        # ],
        [
            "23989399_29216192_32962208",
            [SPLIT_AIR_CONDITIONER],
            "Electrohogar > Climatización > Ventilación",
            1.0,
        ],
        # [
        #     "Climatización/Calefacción/Termos y Calefonts",
        #     [WATER_HEATER],
        #     "Electrohogar > Climatización > Calefacción > Termos y Calefonts",
        #     1.0,
        # ],
        [
            "23989399_53512871",
            [ACCESORIES],
            "Electrohogar > Electrodomésticos Cocina",
            1.0,
        ],
        [
            "89057520_18938454_30849678",
            [PRINTER_SUPPLY],
            "Computación > Impresión > Tintas y Toners",
            1.0,
        ],
        [
            "23989399_75788044_32008261",
            [IRON],
            "Electrohogar > Lavado y Planchado > Planchado",
            1.0,
        ],
        [
            "59721722_76091226_92571610",
            [HAIR_CARE],
            "Belleza y Cuidado Personal > Cuidado Personal > Secadores de Pelo",
            1.0,
        ],
        [
            "59721722_76091226_89836448",
            [HAIR_CARE],
            "Belleza y Cuidado Personal > Cuidado Personal > Alisadores y Onduladores",
            1.0,
        ],
    ]

    @classmethod
    def categories(cls):
        cats = []
        for entry in cls.category_paths:
            for cat in entry[1]:
                if cat not in cats:
                    cats.append(cat)
        return cats

    @classmethod
    def discover_urls_for_category(cls, category, extra_args=None):
        return [category]

    @classmethod
    def discover_urls_for_keyword(cls, keyword, threshold, extra_args=None):
        extra_args = extra_args or {}
        session = session_with_proxy(extra_args)
        session.headers["User-Agent"] = extra_args.get("user_agent", cls.USER_AGENTS[0])
        session.headers["tenant"] = cls.tenant
        product_urls = []

        query_url = (
            "https://529cv9h7mw-dsn.algolia.net/1/indexes/*/"
            "queries?x-algolia-application-id=529CV9H7MW&x-"
            "algolia-api-key=c6ab9bc3e19c260e6bad42abe143d5f4"
        )

        query_params = {
            "requests": [
                {
                    "indexName": "campaigns_production",
                    "params": "query={}&hitsPerPage=1000".format(keyword),
                }
            ]
        }

        response = session.post(query_url, json.dumps(query_params))
        data = json.loads(response.text)

        if not data["results"][0]["hits"]:
            return []

        for entry in data["results"][0]["hits"]:
            product_url = "https://www.lider.cl/catalogo/product/sku/{}/{}".format(
                entry["sku"], entry.get("slug", "a")
            )
            product_urls.append(product_url)

            if len(product_urls) == threshold:
                return product_urls

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        products = {}
        query_url = "https://www.lider.cl/orchestra/graphql/browse"
        path = Path(__file__).with_name("lider_request.txt")
        with path.open("r") as f:
            graphql_query = f.read()

        for e in cls.category_paths:
            category_id, local_categories, section_name, category_weight = e

            if category not in local_categories:
                continue

            page = 1
            fast_mode = extra_args.get("fast_mode", False)
            idx = 1

            while True:
                print(page)

                graphql_variables = {
                    "page": page,
                    "prg": "desktop",
                    "catId": category_id,
                    "sort": "best_match",
                    "ps": 44,
                    "fetchMarquee": True,
                    "fetchSkyline": True,
                    "fetchSbaTop": False,
                    "fetchGallery": False,
                    "fetchDac": False,
                    "tenant": "CHILE_EA_GLASS",
                }

                if fast_mode:
                    graphql_variables["facet"] = "ss_sellertype:Lider"

                graphql_request_body = {
                    "query": graphql_query,
                    "variables": graphql_variables,
                }

                tries = 0
                cf_session = False

                while True:
                    extra_args = extra_args or {}

                    if cf_session:
                        session = cf_session_with_proxy(extra_args)
                    else:
                        session = session_with_proxy(extra_args)

                    session.headers = {
                        "Content-Type": "application/json",
                        "User-Agent": cls.USER_AGENTS[tries],
                        "x-o-bu": "LIDER-CL",
                        "x-o-mart": "B2C",
                        "x-o-vertical": "EA",
                        "X-APOLLO-OPERATION-NAME": "Browse",
                    }
                    try:
                        response = session.post(query_url, json=graphql_request_body)
                        data = json.loads(response.text)
                        products_data = data["data"]["search"]["searchResult"][
                            "itemStacks"
                        ][0]["itemsV2"]
                        tries = 0
                        break
                    except Exception as e:
                        exception = e

                        if cf_session:
                            cf_session = False
                            tries += 1
                        else:
                            cf_session = True

                    if tries > len(cls.USER_AGENTS) - 1:
                        raise exception

                if not products_data:
                    break

                for entry in products_data:
                    product_url = f"https://www.lider.cl{entry['canonicalUrl']}"
                    name = f"{entry['brand']} {entry['name']}"
                    key = entry["offerId"]

                    if not fast_mode and key in products:
                        products[key].positions.append((section_name, idx))
                        idx += 1
                    else:
                        price_info = entry["priceInfo"]
                        normal_price = Decimal(price_info["currentPrice"]["price"])
                        sku = entry["usItemId"]
                        picture_urls = [
                            img["url"]
                            for img in entry["imageInfo"]["allImages"]
                            if validators.url(img["url"])
                        ]
                        seller_name = entry["sellerName"]
                        seller = None if seller_name == "Lider" else seller_name
                        stock = (
                            -1
                            if (
                                entry["availabilityStatusV2"]["value"] == "IN_STOCK"
                                and seller_name == "Lider"
                            )
                            else 0
                        )
                        description_value = entry["shortDescription"]
                        description = (
                            html_to_markdown(description_value)
                            if description_value
                            else None
                        )

                        p = Product(
                            name,
                            cls.__name__,
                            category,
                            product_url,
                            product_url,
                            key,
                            stock,
                            normal_price,
                            normal_price,
                            "CLP",
                            sku=sku,
                            picture_urls=picture_urls,
                            description=description,
                            seller=seller,
                        )

                        if not fast_mode:
                            p.positions = [(section_name, idx)]
                            idx += 1

                        products[key] = p

                page += 1

        return list(products.values())

    @classmethod
    def banners(cls, extra_args=None):
        extra_args = extra_args or {}
        base_url = "https://apps.lider.cl/catalogo/bff/banners?v=2"
        destination_url_base = "https://www.lider.cl/{}"
        session = session_with_proxy(extra_args)
        session.headers["User-Agent"] = cls.USER_AGENTS[0]
        banners = []
        response = session.get(base_url)

        banners_json = json.loads(response.text)
        sliders = banners_json["bannersHome"]

        for idx, slider in enumerate(sliders):
            destination_urls = [destination_url_base.format(slider["link"])[:250]]
            picture_url = slider["backgroundDesktop"]
            if not picture_url.startswith("http"):
                picture_url = "https://apps.lider.cl/landing/" + picture_url

            banners.append(
                {
                    "url": destination_url_base.format(""),
                    "picture_url": picture_url,
                    "destination_urls": destination_urls,
                    "key": picture_url,
                    "position": idx + 1,
                    "section": bs.HOME,
                    "subsection": bs.HOME,
                    "type": bs.SUBSECTION_TYPE_HOME,
                }
            )

        if not banners:
            raise Exception(
                "No banners for Home section: " + destination_url_base.format("")
            )

        return banners
