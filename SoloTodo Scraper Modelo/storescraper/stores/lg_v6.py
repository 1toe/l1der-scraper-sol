import json
import logging
import urllib
import time
from bs4 import BeautifulSoup

from decimal import Decimal

from storescraper.product import Product
from storescraper.store import Store
from storescraper.utils import html_to_markdown, session_with_proxy


class LgV6(Store):
    base_url = "https://www.lg.com"
    region_code = property(lambda self: "Subclasses must implement this")
    currency = "USD"
    price_approximation = "0.01"
    skip_products_without_price = False
    endpoint_url = (
        "https://lgcorporationproduction0fxcu0qx.org.coveo.com/rest/search/v2"
    )

    @classmethod
    def categories(cls):
        cats = []
        for entry in cls._category_paths():
            if entry[1] not in cats:
                cats.append(entry[1])
        return cats

    @classmethod
    def discover_urls_for_category(cls, category, extra_args=None):
        category_paths = cls._category_paths()
        session = session_with_proxy(extra_args)
        session.headers["Authorization"] = "Bearer {}".format(extra_args["coveo_token"])
        discovered_urls = []
        page_size = 50

        for category_id, local_category in category_paths:
            if local_category != category:
                continue
            page = 0
            while True:
                payload = {
                    "aq": '@ec_sub_category_id=="{0}" OR @ec_category_id=="{0}"'.format(
                        category_id
                    ),
                    "searchHub": "{}-B2C-Listing".format(cls.region_code),
                    "numberOfResults": page_size,
                    "firstResult": page * page_size,
                }
                results_unavailable = 0
                json_response = None

                while results_unavailable < 5:
                    response = session.post(cls.endpoint_url, json=payload)
                    json_response = response.json()

                    if "results" in json_response:
                        break

                    results_unavailable += 1
                    time.sleep(30)

                product_entries = json_response["results"]

                if not product_entries:
                    if page == 0:
                        logging.warning("Empty category: {}".format(category_id))
                    break

                for product_entry in product_entries:
                    for subproduct_entry in product_entry["childResults"] + [
                        product_entry
                    ]:
                        is_active = (
                            "ACTIVE" in subproduct_entry["raw"]["ec_model_status_code"]
                        )
                        if cls.skip_products_without_price:
                            price = Decimal(
                                subproduct_entry["raw"].get("ec_price", 0)
                            ) or Decimal(subproduct_entry["raw"].get("ec_msrp", 0))
                            if not price or not is_active:
                                continue

                        if "ec_model_url_path" not in subproduct_entry["raw"]:
                            continue

                        product_url = (
                            cls.base_url + subproduct_entry["raw"]["ec_model_url_path"]
                        )
                        # if subproduct_entry['raw']['ec_where_to_buy_flag'] == 'N' and is_active:
                        #     print(subproduct_entry['raw']['ec_model_id'], subproduct_entry['raw']['ec_sku'], product_url, sep='¬')
                        discovered_urls.append(product_url)
                page += 1

        return discovered_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)

        response = session.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        picture_urls = [
            "https://www.lg.com" + urllib.parse.quote(x["data-large-d"])
            for x in soup.find_all("a", "c-gallery__item")
            if "data-large-d" in x.attrs
        ]
        if not picture_urls:
            standalone_picture_tag = soup.find("link", {"as": "image"})
            if standalone_picture_tag:
                picture_urls = ["https://www.lg.com" + standalone_picture_tag["href"]]

        session.headers["Authorization"] = "Bearer {}".format(extra_args["coveo_token"])
        path = urllib.parse.urlparse(url).path
        payload = {
            "aq": '@ec_model_url_path=="{}"'.format(path),
            "searchHub": "{}-B2C-Listing".format(cls.region_code),
            "numberOfResults": 10,
            "firstResult": 0,
        }
        response = session.post(cls.endpoint_url, json=payload)
        json_data = response.json()["results"][0]["raw"]
        model_id = json_data["ec_model_id"]
        name = "{} - {}".format(
            json_data["ec_sales_model_code"], json_data.get("systitle", "")
        )

        # Unavailable products do not have a price, but we still need to
        # return them by default because the Where To Buy (WTB) system
        # needs to consider all products, so use zero as default.
        price = Decimal(0)

        for price_key in ["ec_price", "ec_msrp"]:
            if price_key not in json_data:
                continue

            price_value = Decimal(json_data[price_key])

            if price_value:
                price = price_value.quantize(Decimal(cls.price_approximation))
                break

        if cls.skip_products_without_price and not price:
            return []

        is_active = "ACTIVE" in json_data["ec_model_status_code"]
        is_in_stock = json_data.get("ec_stock_status", "OUT_OF_STOCK") == "IN_STOCK"

        if is_in_stock and is_active:
            stock = -1
        else:
            stock = 0

        section_path_components = []

        for i in range(1, 5):
            section_key = "ec_classification_flag_lv_{}".format(i)

            if section_key not in json_data:
                continue

            section_path_components.append(json_data[section_key])

        if section_path_components:
            section_path = " > ".join(section_path_components)
        else:
            section_path = "N/A"

        positions = [(section_path, 1)]
        sku = json_data["ec_sku"]

        pdp_data = soup.find("div", {"id": "pdp-overview-section"})

        if pdp_data:
            description = str(pdp_data).replace('="/', '="https://www.lg.com/')
        else:
            description = None

        reviews_endpoint = (
            "https://api.bazaarvoice.com/data/display/0.2alpha/product/summary?PassKey="
            "caLe64uePnBm2AJobXW3AWGdiTwA5fUMHMrBjNTAPTd8c&productid={}"
            "&contentType=reviews&rev=0&contentlocale=es*,es_CL".format(model_id)
        )
        reviews_json = session.get(reviews_endpoint).json()["reviewSummary"]
        review_count = reviews_json["numReviews"]
        review_avg_score = reviews_json["primaryRating"]["average"]

        return [
            Product(
                name[:250],
                cls.__name__,
                category,
                url,
                url,
                model_id,
                stock,
                price,
                price,
                cls.currency,
                sku=sku,
                picture_urls=picture_urls,
                part_number=sku,
                positions=positions,
                allow_zero_prices=not cls.skip_products_without_price,
                description=description,
                review_count=review_count,
                review_avg_score=review_avg_score,
            )
        ]

    @classmethod
    def _category_paths(cls):
        raise NotImplementedError("Subclasses must implement this method")

    @classmethod
    def preflight(cls, extra_args=None):
        session = session_with_proxy(extra_args)
        coveo_token_url = (
            "https://www.lg.com/{}/jcr:" "content.coveoToken.json"
        ).format(cls.region_code.lower())
        response = session.get(coveo_token_url)
        json_response = response.json()
        coveo_token = json_response["token"]
        return {"coveo_token": coveo_token}

    def string_to_dict(input_string):
        entries = input_string.split("};")

        result = []

        for entry in entries:
            entry = entry.strip().lstrip("{")
            elements = entry.split(", ")
            entry_dict = {}

            for element in elements:
                try:
                    key, value = element.split("=", 1)
                    entry_dict[key] = value
                except ValueError:
                    continue

            result.append(entry_dict)

        return result
