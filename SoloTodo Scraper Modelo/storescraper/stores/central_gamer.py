import logging
from decimal import Decimal

from bs4 import BeautifulSoup

from storescraper.categories import (
    MOTHERBOARD,
    COMPUTER_CASE,
    CPU_COOLER,
    POWER_SUPPLY,
    MONITOR,
    HEADPHONES,
    MOUSE,
    KEYBOARD,
    GAMING_CHAIR,
    PROCESSOR,
    VIDEO_CARD,
    RAM,
    SOLID_STATE_DRIVE,
    STEREO_SYSTEM,
)
from storescraper.product import Product
from storescraper.store_with_url_extensions import StoreWithUrlExtensions
from storescraper.utils import session_with_proxy, remove_words, html_to_markdown


class CentralGamer(StoreWithUrlExtensions):
    url_extensions = [
        ["componentes-pc/almacenamiento", SOLID_STATE_DRIVE],
        ["componentes-pc/fuentes-de-poder", POWER_SUPPLY],
        ["componentes-pc/gabinetes-gamer", COMPUTER_CASE],
        ["componentes-pc/placas-madre", MOTHERBOARD],
        ["componentes-pc/procesadores", PROCESSOR],
        ["componentes-pc/memorias-ram", RAM],
        ["componentes-pc/tarjetas-de-video", VIDEO_CARD],
        ["componentes-pc/refrigeracion-pc", CPU_COOLER],
        ["perifericos/audifonos-gamer", HEADPHONES],
        ["perifericos/mouse-gamer", MOUSE],
        ["perifericos/parlantes", STEREO_SYSTEM],
        ["perifericos/teclado-gamer", KEYBOARD],
        ["monitores/monitores-gamer", MONITOR],
        ["mobiliario-gamer/sillas-gamer", GAMING_CHAIR],
        ["mobiliario-gamer/sillones-gamer", GAMING_CHAIR],
    ]

    @classmethod
    def discover_urls_for_url_extension(cls, url_extension, extra_args=None):
        session = session_with_proxy(extra_args)
        product_urls = []
        page = 1
        while True:
            if page > 10:
                raise Exception("page overflow: " + url_extension)
            url_webpage = "https://centralgamer.cl/{}/page/{}".format(
                url_extension, page
            )
            print(url_webpage)
            data = session.get(url_webpage).text
            soup = BeautifulSoup(data, "lxml")
            # import ipdb

            # ipdb.set_trace()
            product_containers = soup.findAll("div", "product-wrapper")
            if not product_containers:
                if page == 1:
                    logging.warning("Empty category: " + url_extension)
                break
            for container in product_containers:
                product_url = container.find("a")["href"]
                product_urls.append(product_url)
            page += 1
        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        response = session.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        name = soup.find("h2", "heading").text
        key = soup.find("link", {"rel": "shortlink"})["href"].split("?p=")[-1]
        stock_text = soup.find("meta", {"property": "og:availability"})["content"]
        stock = -1 if stock_text == "instock" else 0
        prices_html_tag = soup.find("div", "precio-info-raw")
        prices_html = BeautifulSoup(prices_html_tag.text, "lxml")
        price_tags = prices_html.findAll("span", "woocommerce-Price-amount")
        normal_price = Decimal(remove_words(price_tags[0].text))
        offer_price = Decimal(remove_words(price_tags[1].text))
        sku = soup.find("span", "sku").text.strip()
        picture_tags = soup.findAll("div", "swiper-slide zoom")
        picture_urls = [x["data-src"] for x in picture_tags]
        description = html_to_markdown(str(soup.find("div", "entry-product-section")))

        p = Product(
            name,
            cls.__name__,
            category,
            url,
            url,
            key,
            stock,
            normal_price,
            offer_price,
            "CLP",
            sku=sku,
            part_number=sku,
            picture_urls=picture_urls,
            description=description,
        )
        return [p]
