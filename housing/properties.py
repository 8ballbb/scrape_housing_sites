from .utils import error_handler
from typing import Union
import re
from bs4 import BeautifulSoup
import requests


def get_property_features(soup: BeautifulSoup) -> None:
    features = ". ".join([item.text for item in soup.find_all(
        "li", 
        attrs={
            "class": re.compile("^PropertyDetailsList__PropertyDetailsListItem.*")})])
    return features


def get_page_views(soup: BeautifulSoup) -> str:
    stats = soup.find_all(
        "p", 
        attrs={"class": re.compile("^Statistics__StyledLabel.*")})
    views = int(stats[1].text.replace(",", ""))
    return views


def get_description(soup: BeautifulSoup) -> Union[str, None]:
    desc = soup.find(
            "div", 
            attrs={"class": re.compile("^PropertyPage__StandardParagraph.*")}).text
    return desc


def get_static_soup(headers: dict, url: str) -> Union[BeautifulSoup, None]:
    """Make request to page and return BeautifulSoup object"""
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, features="lxml")
        else:
            soup = None
    except requests.exceptions.ConnectionError as e:
        print(e, "-static-", url)
        soup = None
    except requests.exceptions.ChunkedEncodingError as e:
        print(e, "-static-", url)
        soup = None
    return soup


def scrape_property_page(headers: dict, url: str) -> tuple:
    """Scrape property page data"""
    soup = get_static_soup(headers, url)
    if soup is not None:
        views = error_handler(get_page_views, soup)
        desc = error_handler(get_description, soup)
        features = error_handler(get_property_features, soup)
        return views, desc, features
    else:
        return None, None, None
