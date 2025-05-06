from bs4 import BeautifulSoup

from .abcdin import AbcDin
from storescraper import banner_sections as bs
from storescraper.utils import session_with_proxy


class LaPolar(AbcDin):
    base_url = "https://www.lapolar.cl"
    site_name = "LaPolar"
