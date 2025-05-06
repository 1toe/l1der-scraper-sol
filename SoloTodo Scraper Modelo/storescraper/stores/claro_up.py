import csv
from decimal import Decimal

from storescraper.categories import (
    CELL,
)
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import session_with_proxy


class ClaroUp(StoreWithUrlExtensions):
    url_extensions = [
        ("https://www.clarochile.cl/personas/claro-up/", CELL),
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args=None):
        return [url_extension]

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        session = session_with_proxy(extra_args)
        endpoint = (
            "https://migracion.clarochilepromociones.com/ofertaPlanConEquipo/info.php"
        )
        response = session.get(endpoint)
        json_response = response.json()
        print(endpoint)

        plans_dict = {
            "claroUpPlanL": "Claro Plan MAX L LIBRE",
            "claroUpPlanXl": "Claro Plan MAX XL LIBRE",
            "claroUpPlanLibrePro": "Claro Plan MAX LIBRE PRO",
        }
        products = []

        for plan_key, cell_plan in plans_dict.items():
            plan_entry = json_response[plan_key]
            reader = csv.reader(plan_entry.split("\r\n")[1:])
            # ['id', 'brand ', 'model', 'priceBefore', 'priceAfter (Pie)', 'fee', 'price', 'discount', 'image',
            # 'storage', 'screen', 'sae', 'cameraFrontal', 'cameraTrasera', 'urlSae', 'exclusive', 'out', 'urlTienda']
            for line in reader:
                base_name = f"{line[1]} {line[2]}"
                key = f"{base_name} - {cell_plan}"
                price = Decimal(line[4])
                cell_monthly_payment = Decimal(line[6])
                picture_urls = [line[8]]

                p = Product(
                    base_name,
                    cls.__name__,
                    category,
                    url,
                    url,
                    key,
                    -1,
                    price,
                    price,
                    "CLP",
                    cell_monthly_payment=cell_monthly_payment,
                    picture_urls=picture_urls,
                    cell_plan_name=cell_plan,
                    allow_zero_prices=True,
                )
                products.append(p)

        return products
