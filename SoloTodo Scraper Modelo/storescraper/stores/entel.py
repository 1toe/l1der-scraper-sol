import json

from collections import defaultdict

from bs4 import BeautifulSoup
from decimal import Decimal

from storescraper.categories import CELL, CELL_PLAN
from storescraper.product import Product
from storescraper.store import Store
from storescraper.utils import session_with_proxy


class Entel(Store):
    prepago_url = "https://www.entel.cl/prepago/"
    planes_url = "https://www.entel.cl/planes/oferta-portabilidad/"

    @classmethod
    def categories(cls):
        return [CELL, CELL_PLAN]

    @classmethod
    def discover_entries_for_category(cls, category, extra_args=None):
        session = session_with_proxy(extra_args)
        session.headers["Accept"] = "application/json"
        product_entries = defaultdict(lambda: [])

        if category == CELL:
            # Contrato

            endpoints = [
                "equipo-plan",
                "celulares",
                # "ofertas",
                "equipos-5g",
                "seminuevos",
            ]

            for endpoint in endpoints:
                json_url = (
                    "https://miportal.entel.cl/personas/catalogo/{}?"
                    "No=0&Nrpp=1000&subPath=main%5B1%5D".format(endpoint)
                )
                response = session.get(json_url)

                json_product_list = json.loads(response.text)["records"]

                for idx, device in enumerate(json_product_list):
                    product_url = (
                        "https://miportal.entel.cl/personas/"
                        "producto{}".format(device["detailsAction"]["recordState"])
                    )

                    # We mostly don't care about the exact position, just
                    # merge the endpoints data
                    product_entries[product_url].append(
                        {
                            "category_weight": 1,
                            "section_name": endpoint,
                            "value": idx + 1,
                        }
                    )

        if category == CELL_PLAN:
            product_entries[cls.prepago_url].append(
                {"category_weight": 1, "section_name": "Planes", "value": 1}
            )
            product_entries[cls.planes_url].append(
                {"category_weight": 1, "section_name": "Planes", "value": 2}
            )

        return product_entries

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        products = []
        if url == cls.prepago_url:
            # Plan Prepago
            products.append(
                Product(
                    "Entel Prepago",
                    cls.__name__,
                    category,
                    url,
                    url,
                    "Entel Prepago",
                    -1,
                    Decimal(0),
                    Decimal(0),
                    "CLP",
                    allow_zero_prices=True,
                )
            )

        elif url == cls.planes_url:
            # Plan Postpago
            products.extend(cls._plans(extra_args))
        elif "miportal.entel.cl" in url:
            # Equipo postpago
            products.extend(cls._celular_postpago(url, extra_args))
        else:
            raise Exception("Invalid URL: " + url)
        return products

    @classmethod
    def _plans(cls, extra_args):
        session = session_with_proxy(extra_args)
        response = session.get(cls.planes_url)
        soup = BeautifulSoup(response.text, "lxml")
        plans_container = soup.find("swiper-container", {"id": "cards-planes-movil"})
        plans = plans_container.findAll("swiper-slide")
        products = []

        for plan in plans:
            plan_data = json.loads(
                plan.find("eds-card-movil-2").get("eds-btn-detail-complete")
            )["data"]
            base_plan_name = plan_data["product_name"]
            price = Decimal(plan_data["product_price"])

            if price == 0:
                continue

            for suffix in ["", " Portabilidad"]:
                name = f"{base_plan_name}{suffix}"
                products.append(
                    Product(
                        name,
                        cls.__name__,
                        CELL_PLAN,
                        cls.planes_url,
                        cls.planes_url,
                        name,
                        -1,
                        price,
                        price,
                        "CLP",
                    )
                )
        return products

    @classmethod
    def _celular_postpago(cls, url, extra_args):
        session = session_with_proxy(extra_args)

        soup = BeautifulSoup(session.get(url).text, "lxml")
        product_detail_container = soup.find("div", {"id": "productDetail"})

        if not product_detail_container:
            # For the case of https://miportal.entel.cl/personas/producto/
            # prod1410051 that displays a blank page
            return []

        raw_json = product_detail_container.find("script").string

        try:
            json_data = json.loads(raw_json)
        except json.decoder.JSONDecodeError:
            return []

        if json_data["isAccessory"]:
            return []

        stock_dict = {x["skuId"]: x["stockDelivery"] for x in json_data["skuViews"]}
        products = []

        for variant in json_data["renderSkusBean"]["skus"]:
            variant_name = variant["skuName"]
            variant_sku = variant["skuId"]
            stock = stock_dict[variant_sku]

            refurbished_blacklist = ["semi", "renovado"]

            for blacklist in refurbished_blacklist:
                if blacklist in variant_name.lower():
                    condition = "https://schema.org/RefurbishedCondition"
                    break
            else:
                condition = "https://schema.org/NewCondition"

            plans_url = (
                "https://miportal.entel.cl/"
                "restpp/equipments/prices/{}".format(variant_sku)
            )

            plans_data = json.loads(session.get(plans_url).text)["response"]["Prices"]

            suffix_dict = {"Portabilidad": " Portabilidad", "Venta": ""}

            for plan in plans_data:
                if plan["orderArea"] == "Activacion de Linea":
                    continue

                if not plan["showInPlanList"]:
                    continue

                plan_name = (
                    plan["planDisplayName"].strip() + suffix_dict[plan["orderArea"]]
                )

                price = Decimal(round(plan["priceIVA"]))

                products.append(
                    Product(
                        variant_name,
                        cls.__name__,
                        CELL,
                        url,
                        url,
                        "{} - {}".format(variant_sku, plan_name),
                        stock,
                        price,
                        price,
                        "CLP",
                        sku=variant_sku,
                        cell_monthly_payment=Decimal(0),
                        cell_plan_name=plan_name,
                        condition=condition,
                        allow_zero_prices=True,
                    )
                )

            # Prepago
            price_container = variant["skuPrice"]
            if not price_container:
                continue

            price = Decimal(price_container).quantize(0)
            product_data = json.loads(
                soup.find("script", {"type": "application/ld+json"}).text
            )

            if (
                "offers" in product_data
                and "AggregateOffer" in product_data["offers"]["@type"]
            ):
                offer_price = Decimal(product_data["offers"]["lowPrice"]).quantize(0)
            else:
                offer_price = price

            product = Product(
                variant_name,
                cls.__name__,
                CELL,
                url,
                url,
                "{} - Entel Prepago".format(variant_sku),
                stock,
                price,
                offer_price,
                "CLP",
                sku=variant_sku,
                cell_monthly_payment=Decimal(0),
                cell_plan_name="Entel Prepago",
                condition=condition,
            )
            products.append(product)

        return products
