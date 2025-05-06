import json
from collections import defaultdict
from decimal import Decimal

import pyjson5
from bs4 import BeautifulSoup

from storescraper.categories import CELL, CELL_PLAN
from storescraper.product import Product
from storescraper.store import Store
from storescraper.utils import session_with_proxy, remove_words


class Claro(Store):
    planes_url = "https://api-prod-cl.prod.clarodigital.net/api/CL_MS_FE_PLANES_DESTACADOS/getPlanesDestacadosXCategoria"
    prepago_url = (
        "https://www.clarochile.cl/personas/servicios/servicios-moviles/prepago/"
    )
    equipos_url = "https://www.clarochile.cl/personas/ofertaplanconequipo/"

    combinations = [
        ("", "valor_contado_planes", None),
        (" Cuotas", "papcn_pc_valor_cuota_inicial", "papcn_pc_12_cuotas_de"),
        (" Portabilidad", "valor_contado_planes", None),
        (" Portabilidad Cuotas", "pap_pc_valor_cuota_inicial", "pap_pc_12_cuotas_de"),
    ]
    include_prepago_price = True

    @classmethod
    def categories(cls):
        return [CELL, CELL_PLAN]

    @classmethod
    def discover_entries_for_category(cls, category, extra_args=None):
        discovered_entries = defaultdict(lambda: [])

        if category == CELL_PLAN:
            discovered_entries[cls.prepago_url].append(
                {"category_weight": 1, "section_name": "Planes", "value": 1}
            )

            discovered_entries[cls.planes_url].append(
                {"category_weight": 1, "section_name": "Planes", "value": 2}
            )
        if category == CELL:
            cell_urls = cls._discover_cells(extra_args)
            for idx, cell_url in enumerate(cell_urls):
                discovered_entries[cell_url].append(
                    {"category_weight": 1, "section_name": "Equipos", "value": idx + 1}
                )

        return discovered_entries

    @classmethod
    def _discover_cells(cls, extra_args=None):
        product_urls = []
        session = session_with_proxy(extra_args)
        session.headers["User-Agent"] = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )
        session.headers["Accept-Language"] = "en"
        offset = 0

        while True:
            category_url = (
                "https://tienda.clarochile.cl/CategoryDisplay"
                "?facet_1=ads_f11503_ntk_cs%3A%22Portando+un"
                "+Plan%22&categoryId=3074457345616686668&"
                "storeId=10151&beginIndex={}".format(offset)
            )
            print(category_url)
            soup = BeautifulSoup(session.get(category_url).text, "html5lib")

            listing = soup.find("div", "product_listing_container")

            if not listing:
                if offset == 0:
                    raise Exception("Empty list")
                break

            containers = listing.findAll("div", "product")[1:]

            if not containers:
                if offset == 0:
                    raise Exception("Empty list")
                break

            for container in containers:
                product_url = container.find_all("a")[1]["href"]
                product_urls.append(product_url)

            offset += 12

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        products = []
        if url == cls.prepago_url:
            # Plan Prepago
            p = Product(
                "Claro Prepago",
                cls.__name__,
                category,
                url,
                url,
                "Claro Prepago",
                -1,
                Decimal(0),
                Decimal(0),
                "CLP",
                allow_zero_prices=True,
            )
            products.append(p)
        elif url == cls.planes_url:
            # Plan Postpago
            planes = cls._planes(url, extra_args)
            products.extend(planes)
        else:
            # Celular
            cells = cls._celular_postpago(url, category, extra_args)
            products.extend(cells)
        return products

    @classmethod
    def _planes(cls, url, extra_args):
        payload = {
            "fc_tipo_plan": "PLN",
            "fi_servicio": 60,
            "fc_tipo": "Personas-Servicios-Moviles-PlanesMoviles-Individuales",
            "fc_familia": "60",
        }
        session = session_with_proxy(extra_args)
        response = json.loads(session.post(url, json=payload).text)
        products = []
        portabilidad_modes = [
            "",
            " Portabilidad",
        ]
        leasing_modes = [" (sin cuota de arriendo)", " (con cuota de arriendo)"]

        for plan in response:
            plan_name = plan["fc_NOMBRE"].strip()
            plan_name = " ".join(plan_name.split())
            plan_url = f"https://www.clarochile.cl{plan['fc_URL_PLANES']}"

            for portability_mode in portabilidad_modes:
                normal_price = plan["fc_PRECIO_TACHADO"]

                if normal_price != "":
                    plan_price = Decimal(normal_price)
                else:
                    plan_price = Decimal(plan["fi_PRECIO_PLAN"])

                for leasing_mode in leasing_modes:
                    name = "{}{}{}".format(plan_name, portability_mode, leasing_mode)

                    products.append(
                        Product(
                            name,
                            cls.__name__,
                            CELL_PLAN,
                            plan_url,
                            url,
                            name,
                            -1,
                            plan_price,
                            plan_price,
                            "CLP",
                        )
                    )

        return products

    @classmethod
    def _celular_postpago(cls, url, category, extra_args):
        print(url)
        extra_args = extra_args or {}
        session = session_with_proxy(extra_args)
        session.headers["User-Agent"] = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )
        session.headers["Accept-Language"] = "en"
        res = session.get(url)
        soup = BeautifulSoup(res.text, "html5lib")
        product_id = soup.find("meta", {"name": "pageId"})["content"]
        base_name = soup.find("h1", "main_header").text.strip()
        picture_tag_id = "ProductInfoImage_" + product_id
        picture_urls = [
            "https://tienda.clarochile.cl"
            + soup.find("input", {"id": picture_tag_id})["value"].replace(" ", "%20")
        ]

        category_entries_tag = soup.find("div", {"id": "entitledItem_" + product_id})
        category_entries = json.loads(category_entries_tag.text.replace("'", '"'))

        session.headers["Content-Type"] = (
            "application/x-www-form-urlencoded" "; charset=UTF-8"
        )
        products = []

        for c in category_entries:
            payload = (
                "storeId=10151&langId=-5"
                "&catalogId=10052&catalogEntryId={}"
                "&productId={}&requesttype=ajax".format(c["catentry_id"], product_id)
            )
            res = session.post(
                "https://tienda.clarochile.cl/GetCatalogEntryDetailsByIDView", payload
            )

            data = pyjson5.decode(res.text)["catalogEntry"]

            stock_payload = (
                "storeId=10151&catalogId=10052&quantity=1"
                "&catEntryId={}".format(c["catentry_id"])
            )
            res = session.post(
                "https://tienda.clarochile.cl/AjaxRESTOrderItemAdd", stock_payload
            )
            stock_data = json.loads(res.text.strip()[2:-2])
            if stock_data.get("errorMessageKey", "") == "_ERR_ITEM_INVENTORY_AVALAIBLE":
                stock = 0
            else:
                stock = -1

            combination_type = data["attrSwatchFlujo"]

            combination_types = extra_args.get(
                "combination_types", ["PRE", "PE_LN", "PEB", "PE_PORTA"]
            )

            if combination_type not in combination_types:
                # Renovación or Default
                continue

            price_text = remove_words(data["offerPrice"])
            if not price_text:
                return []
            price = Decimal(price_text)

            attributes = []
            for key, value in c["Attributes"].items():
                attr_label, attr_value = key.split("_|_")
                if attr_label == "Flujo":
                    continue
                attributes.append("{} {}".format(attr_label, attr_value))

            name = "{} ({})".format(base_name, " / ".join(attributes))

            if combination_type == "PRE":
                # Prepago
                products.append(
                    Product(
                        name,
                        cls.__name__,
                        category,
                        url,
                        url,
                        "{} - {}".format(product_id, "Claro Prepago"),
                        stock,
                        price,
                        price,
                        "CLP",
                        cell_plan_name="Claro Prepago",
                        cell_monthly_payment=Decimal(0),
                        picture_urls=picture_urls,
                    )
                )
            elif combination_type == "PE_LN":
                # Línea nueva

                for plan_entry in data["planAssociate"]:
                    cell_plan_name = plan_entry["name"]

                    products.append(
                        Product(
                            name,
                            cls.__name__,
                            category,
                            url,
                            url,
                            "{} - {}".format(product_id, cell_plan_name),
                            stock,
                            price,
                            price,
                            "CLP",
                            cell_plan_name="Claro {}".format(cell_plan_name),
                            cell_monthly_payment=Decimal(0),
                            picture_urls=picture_urls,
                            allow_zero_prices=True,
                        )
                    )
            elif combination_type == "PEB":
                # Portabildiad arriendo
                if data["catentry_field2"] == "":
                    continue
                init_pay = Decimal(data["attrAbonoInit"])
                num_cuotas = Decimal(data["catentry_field2"])
                cell_monthly_payment = ((price - init_pay) / num_cuotas).quantize(0)
                if cell_monthly_payment > Decimal("1000000"):
                    # Prevents error on this page:
                    # https://tienda.clarochile.cl/catalogo/equiposclaro/samsung-s23-128gb-5g-crema-70011692pob
                    # For "Portando un plan" with Plan Max L Libre
                    continue

                for plan_entry in data["planAssociate"]:
                    cell_plan_name = plan_entry["name"] + " Portabilidad Cuotas"

                    products.append(
                        Product(
                            name,
                            cls.__name__,
                            category,
                            url,
                            url,
                            "{} - {}".format(product_id, cell_plan_name),
                            stock,
                            init_pay,
                            init_pay,
                            "CLP",
                            cell_plan_name="Claro {}".format(cell_plan_name),
                            cell_monthly_payment=cell_monthly_payment,
                            picture_urls=picture_urls,
                            allow_zero_prices=True,
                        )
                    )
            elif combination_type == "PE_PORTA":
                # Portabilidad sin arriendo

                for plan_entry in data["planAssociate"]:
                    cell_plan_name = plan_entry["name"] + " Portabilidad"

                    products.append(
                        Product(
                            name,
                            cls.__name__,
                            category,
                            url,
                            url,
                            "{} - {}".format(product_id, cell_plan_name),
                            stock,
                            price,
                            price,
                            "CLP",
                            cell_plan_name="Claro {}".format(cell_plan_name),
                            cell_monthly_payment=Decimal(0),
                            picture_urls=picture_urls,
                            allow_zero_prices=True,
                        )
                    )
            elif combination_type == "":
                # Default (Accesories)
                products.append(
                    Product(
                        name,
                        cls.__name__,
                        category,
                        url,
                        url,
                        str(product_id),
                        stock,
                        price,
                        price,
                        "CLP",
                        picture_urls=picture_urls,
                    )
                )
            else:
                raise Exception("Invalid switch:" + combination_type)

        return products
