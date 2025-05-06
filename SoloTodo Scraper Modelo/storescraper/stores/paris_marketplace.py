from storescraper.categories import TELEVISION
from storescraper.stores import Paris
from storescraper.store import Store


class ParisMarketplace(Store):
    category_paths = [
        "https://www.paris.cl/refrigerador-bottom-mount-290l-all-around-cooling-MKQRIMTEY5.html",
        "https://www.paris.cl/refrigerador-top-mount-freezer-234l-all-around-cooling-MKZ0MSVJXO.html",
        "https://www.paris.cl/refrigerador-bottom-mount-de-311l-all-around-cooling-MKN5ZPW6WK.html",
        "https://www.paris.cl/refrigerador-top-mount-freezer-341l-space-max-MK68SEHDQS.html",
        "https://www.paris.cl/refrigerador-top-mount-freezer-407l-space-max-MK7MKKUFKK.html",
        "https://www.paris.cl/refrigerador-bottom-mount-freezer-321l-space-max-MKSP7RC4KK.html",
        "https://www.paris.cl/refrigerador-bottom-mount-freezer-328l-space-max-MKXPC3Y9R6.html",
        "https://www.paris.cl/refrigerador-top-mount-freezer-391-l-space-max-MKR5W06Q1N.html",
        "https://www.paris.cl/refrigerador-top-mount-freezer-255l-all-around-cooling-MKCRA1M9Q6.html",
        "https://www.paris.cl/refrigerador-bottom-mount-462l-freezer-space-max-MK83B6ESB2.html",
        "https://www.paris.cl/refrigerador-top-mount-freezer-384l-space-max-MKF9HNZ5C6.html",
        "https://www.paris.cl/samsung-refrigerador-384-l-top-freezer-MKKO4PYBJP.html",
    ]

    @classmethod
    def categories(cls):
        return [TELEVISION]

    @classmethod
    def discover_entries_for_category(cls, category, extra_args=None):
        product_entries = {}

        for url in cls.category_paths:
            product_entries[url] = []

        return product_entries

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        products = Paris.products_for_url(url, category, extra_args)

        for product in products:
            product.store = cls.__name__
            product.seller = None
            product.stock = -1

        return products
