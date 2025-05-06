from storescraper.categories import TELEVISION
from storescraper.store import Store
from storescraper.stores import Falabella


class FalabellaMarketplace(Store):
    category_paths = [
        "https://www.falabella.com/falabella-cl/product/131934511/LED-Smart-TV-32-T4202-HD-Tizen%E2%84%A2-Samsung-(2020)/131934512",
        "https://www.falabella.com/falabella-cl/product/138777627/Samsung-43-FHD-T5203-Smart-TV-2024/138777628",
        "https://www.falabella.com/falabella-cl/product/133213824/LED-Smart-TV-43-DU7000-4K-UHD-Tizen%E2%84%A2-Samsung-(2024)/133213825",
        "https://www.falabella.com/falabella-cl/product/135836256/LED-Smart-TV-43-CU7090-4K-UHD-Tizen%E2%84%A2-Samsung-(2024)/135836257",
        "https://www.falabella.com/falabella-cl/product/140543658/Smart-TV-Samsung-50''-Crystal-UHD-4K-CU8000/140543659",
        "https://www.falabella.com/falabella-cl/product/140763002/Smart-TV-Samsung-Led-50-DU8000-4K-Crystal-UHD/140763003",
        "https://www.falabella.com/falabella-cl/product/131934383/LED-Smart-TV-50-DU8000-4K-UHD-Tizen%E2%84%A2-Samsung-(2024)/131934384",
        "https://www.falabella.com/falabella-cl/product/140543696/Smart-TV-Samsung-32''-The-Frame-LS03C-QN32LS03CBGXZS/140543697",
        "https://www.falabella.com/falabella-cl/product/139862043/LED-Samsung-55-DU7000-4K-UHD-Smart-TV-2024/139862044",
        "https://www.falabella.com/falabella-cl/product/140543706/Smart-TV-Samsung-QLED-50-Q65D-Series/140543707",
        "https://www.falabella.com/falabella-cl/product/136242838/QLED-Smart-TV-43-The-Serif-LS01D-4K-Tizen%E2%84%A2-Samsung-(2024)/136242839",
        "https://www.falabella.com/falabella-cl/product/135836702/LED-Smart-TV-65-CU7090-4K-UHD-Tizen%E2%84%A2-Samsung-(2024)/135836703",
        "https://www.falabella.com/falabella-cl/product/136242894/QLED-Smart-TV-50-The-Serif-LS01D-4K-Tizen%E2%84%A2-Samsung-(2024)/136242895",
        "https://www.falabella.com/falabella-cl/product/140543632/Smart-tv-Samsung-QLED-UHD-4K-43-The-Serif/140543633",
        "https://www.falabella.com/falabella-cl/product/140756236/Smart-Tv-Samsung-43'-Neo-Qled-4k-Qn90c/140756237",
        "https://www.falabella.com/falabella-cl/product/130434311/Neo-QLED-Smart-TV-43-QN90D-4K-UHD-Tizen%E2%84%A2-Samsung-(2024)/130434312",
        "https://www.falabella.com/falabella-cl/product/140543646/Smart-TV-50''-The-Frame-LS03B-QN50LS03BAGXZS/140543647",
        "https://www.falabella.com/falabella-cl/product/140543654/Smart-tv-Samsung-43-The-Sero-QN43LS05TAGXSZ/140543655",
        "https://www.falabella.com/falabella-cl/product/140756238/Qled-Samsung-50-The-Serif-4k-Uhd-Smart-Tv-2022/140756239",
        "https://www.falabella.com/falabella-cl/product/142302257/Televisor-Qled-55-Samsung-QN55LS01DAGXZS-Full-HD/142302258",
        "https://www.falabella.com/falabella-cl/product/139475204/PANTALLA-PROFESIONAL-SAMSUNG-50UHD-4K-16-7/139475205",
        "https://www.falabella.com/falabella-cl/product/140543664/Smart-TV-Samsung-QLED-55-QX1-Series/140543665",
        "https://www.falabella.com/falabella-cl/product/140543668/Smart-TV-Samsung-50-Neo-QLED-QN90B-QN50QN90BAGXZS/140543669",
        "https://www.falabella.com/falabella-cl/product/140159399/Smart-Tv-Samsung-Hospitality-Pantalla-Plana-50-UHD/140159400",
        "https://www.falabella.com/falabella-cl/product/136243791/QLED-Smart-TV-55-The-Serif-LS01D-4K-Tizen%E2%84%A2-Samsung-(2024)/136243792",
        "https://www.falabella.com/falabella-cl/product/139404001/Smart-Tv-Samsung-QN55Q65DAGXZS-Pantalla-Plana-55-4K/139404002",
        "https://www.falabella.com/falabella-cl/product/140763065/Smart-Tv-Samsung-55-Class-Ls03d-The-Frame-Series-Qled-4k/140763068",
        "https://www.falabella.com/falabella-cl/product/130433984/QLED-Smart-TV-75-Q70D-4K-UHD-Tizen%E2%84%A2-Samsung-(2024)/130433985",
        "https://www.falabella.com/falabella-cl/product/140543678/Smart-TV-Samsung-QLED-75-Q70D-Series/140543679",
        "https://www.falabella.com/falabella-cl/product/135600184/OLED-Smart-TV-65-S90D-4K-UHD-Tizen%E2%84%A2-Samsung-(2024)/135600185",
        "https://www.falabella.com/falabella-cl/product/130433990/QLED-Smart-TV-85-Q65D-4K-UHD-Tizen%E2%84%A2-Samsung-(2024)/130433991",
        "https://www.falabella.com/falabella-cl/product/140543682/Smart-TV-75''-Samsung-The-Frame-LS03B/140543683",
        "https://www.falabella.com/falabella-cl/product/140756234/Smart-TV-Samsung-OLED-77-S90C-Series/140756235",
        "https://www.falabella.com/falabella-cl/product/130433969/Neo-QLED-Smart-TV-65-QN800D-8K-UHD-Tizen%E2%84%A2-Samsung-(2024)/130433970",
        "https://www.falabella.com/falabella-cl/product/135600088/LED-Smart-TV-98-DU9000-4K-UHD-Tizen%E2%84%A2-Samsung-(2024)/135600089",
        "https://www.falabella.com/falabella-cl/product/130433967/Neo-QLED-Smart-TV-75-QN800D-8K-UHD-Tizen%E2%84%A2-Samsung-(2024)/130433968",
        "https://www.falabella.com/falabella-cl/product/135600300/OLED-Smart-TV-83-S90D-4K-UHD-Tizen%E2%84%A2-Samsung-(2024)/135600301",
        "https://www.falabella.com/falabella-cl/product/141382201/Smart-TV-75-Neo-QLED-8K-QN700B/141382202",
        "https://www.falabella.com/falabella-cl/product/131934509/QLED-Smart-TV-98-Q80C-4K-UHD-Tizen%E2%84%A2-Samsung-(2023)/131934510",
        "https://www.falabella.com/falabella-cl/product/130433965/Neo-QLED-Smart-TV-75-QN900D-8K-UHD-Tizen%E2%84%A2-Samsung-(2024)/130433966",
        "https://www.falabella.com/falabella-cl/product/141382206/Smart-TV-Samsung-85-Neo-QLED-8K-QN900D-Tizen-OS-(2024)/141382207",
        "https://www.falabella.com/falabella-cl/product/140756242/Smart-TV-Samsung-Neo-QLED-85-QN900B-Series/140756244",
        "https://www.falabella.com/falabella-cl/product/135836612/LED-Smart-TV-55-CU7090-4K-UHD-Tizen%E2%84%A2-Samsung-(2024)/135836613",
        "https://www.falabella.com/falabella-cl/product/135836390/LED-Smart-TV-50-CU7090-4K-UHD-Tizen%E2%84%A2-Samsung-(2024)/135836391",
        "https://www.falabella.com/falabella-cl/product/131934383/LED-Smart-TV-50-DU8000-4K-UHD-Tizen%E2%84%A2-Samsung-(2023)/131934384",
        "https://www.falabella.com/falabella-cl/product/131934395/LED-Smart-TV-55-DU8000-4K-UHD-Tizen%E2%84%A2-Samsung-(2024)/131934396",
        "https://www.falabella.com/falabella-cl/product/131934451/Refrigerador-Top-Mount-Freezer-407L-Space-Max/131934452",
        "https://www.falabella.com/falabella-cl/product/131934818/Refrigerador-Top-Mount-Freezer-234L-All-Around-Cooling/131934819",
        "https://www.falabella.com/falabella-cl/product/131934457/Refrigerador-Top-Mount-Freezer-391-L-Space-Max/131934458",
        "https://www.falabella.com/falabella-cl/product/139947897/Refrigerador-Side-by-Side-564L-Gris/139947899",
        "https://www.falabella.com/falabella-cl/product/131934816/Refrigerador-Bottom-Mount-Freezer-328L-Space-Max/131934817",
        "https://www.falabella.com/falabella-cl/product/131934934/Refrigerador-Bottom-Mount-de-311L-All-Around-Cooling/131934935",
        "https://www.falabella.com/falabella-cl/product/131934455/Refrigerador-Top-Mount-Freezer-341L-Space-Max/131934456",
        "https://www.falabella.com/falabella-cl/product/136488156/Refrigerador-Bottom-Mount-290L-All-Around-Cooling/136488157",
        "https://www.falabella.com/falabella-cl/product/132173477/Refrigerador-Bottom-Mount-462L-Freezer-Space-Max/132173478",
        "https://www.falabella.com/falabella-cl/product/136488164/Refrigerador-Top-Mount-Freezer-298L-Space-Max/136488165",
        "https://www.falabella.com/falabella-cl/product/131934453/Refrigerador-Top-Mount-Freezer-384L-Space-Max/131934454",
        "https://www.falabella.com/falabella-cl/product/131934804/Refrigerador-Bottom-Mount-Freezer-321L-Space-Max/131934805",
        "https://www.falabella.com/falabella-cl/product/136373759/Refrigerador-Top-Mount-Freezer-255L-All-Around-Cooling/136373760",
        "https://www.falabella.com/falabella-cl/product/137169524/Samsung-Refrigerador-Top-Mount-Freezer-384-L-con-Space-Max/137169525",
        "https://www.falabella.com/falabella-cl/product/139979004/Refrigerador-Side-by-Side-con-dispensador-560L-Negro/139979005",
        "https://www.falabella.com/falabella-cl/product/137173840/Lavadora-de-carga-superior-8Kg-con-tecnologia-Digital-Inverter/137173842",
        "https://www.falabella.com/falabella-cl/product/137156501/Lavadora-de-carga-superior-9Kg-con-tecnologia-Digital-Inverter/137156502",
        "https://www.falabella.com/falabella-cl/product/136868386/Lavadora-de-carga-superior-13Kg-con-Eco-Bubble/136868387",
        "https://www.falabella.com/falabella-cl/product/133901798/Lavadora-Samsung-de-carga-superior-15Kg-con-Eco-Bubble%E2%84%A2/133901799",
        "https://www.falabella.com/falabella-cl/product/137174739/Lavadora-de-carga-superior-15Kg-con-Eco-Bubble/137174740",
        "https://www.falabella.com/falabella-cl/product/131961882/Lavadora-de-carga-superior-17Kg-con-Eco-Bubble%E2%84%A2-Blanca/131961883",
        "https://www.falabella.com/falabella-cl/product/131935340/Samsung-Lavadora-Secadora-9,5-Kg-6-Kg-con-Eco-Bubble/131935342",
        "https://www.falabella.com/falabella-cl/product/131961874/Samsung-Lavadora-de-carga-superior-17Kg-con-Eco-Bubble%E2%84%A2-WA17CG6441BDZS/131961875",
        "https://www.falabella.com/falabella-cl/product/131935327/Lavadora-Secadora-11Kg-7Kg/131935328",
        "https://www.falabella.com/falabella-cl/product/131961878/Lavadora-de-carga-superior-19Kg-con-Eco-Bubble%E2%84%A2-Blanca/131961879",
        "https://www.falabella.com/falabella-cl/product/131961870/Samsung-Lavadora-de-carga-superior-19Kg-con-Eco-Bubble/131961871",
        "https://www.falabella.com/falabella-cl/product/131935329/Lavadora-Secadora-11-Kg-7-Kg-con-Eco-Bubble%E2%84%A2/131935330",
        "https://www.falabella.com/falabella-cl/product/131961866/Lavavajillas-14-cubiertos-Silver-con-Flexible-3rd-Rack/131961867",
        "https://www.falabella.com/falabella-cl/product/137175938/Lavadora-Secadora-11Kg-7Kg-con-Eco-Bubble/137175939",
        "https://www.falabella.com/falabella-cl/product/131935331/Lavadora-Secadora-12Kg-7Kg-con-Inteligencia-Artificial-en-Panel-de-Control/131935332",
        "https://www.falabella.com/falabella-cl/product/136369498/Lavadora-Secadora-125Kg-7Kg-con-Inteligencia-Artificial-en-Panel-de-Control-Negra/136369499",
        "https://www.falabella.com/falabella-cl/product/131961864/Lavavajillas-14-Cubiertos-con-Smart-Things/131961865",
        "https://www.falabella.com/falabella-cl/product/131961880/Samsung-Lavadora-de-carga-superior-21-Kg-con-SmartThings-WA21CG6886BV/131961881",
        "https://www.falabella.com/falabella-cl/product/136971924/Secadora-9Kg-Por-Bomba-de-Calor/136971930",
        "https://www.falabella.com/falabella-cl/product/131961862/Lavavajillas-Samsung-14-Cubiertos-con-Smart-Things/131961863",
        "https://www.falabella.com/falabella-cl/product/131961886/Lavadora-Samsung-de-carga-superior-22Kg-con-Eco-Bubble/131961887",
        "https://www.falabella.com/falabella-cl/product/131961868/Samsung-Lavadora-de-carga-superior-24Kg-con-Eco-Bubble/131961869",
        "https://www.falabella.com/falabella-cl/product/125277920/Lavadora-Secadora-Bespoke-14Kg-9Kg-con-Inteligencia-Artificial-en-Ecobubble/125277921",
        "https://www.falabella.com/falabella-cl/product/131935337/Samsung-Lavadora-Secadora-20Kg-12Kg-con-Inteligencia-Artificial-en-Panel-de-Control/131935338",
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
        extra_args.update({"bypass_sellers_blacklist": True})

        products = Falabella.products_for_url(
            url, category=category, extra_args=extra_args
        )

        for product in products:
            product.store = cls.__name__
            product.seller = None

        return products
