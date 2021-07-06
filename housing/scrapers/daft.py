from datetime import datetime
from math import ceil
import re
from time import sleep
from typing import Union, Iterable
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import requests
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm


def browser_options() -> Options:
    """Set web driver options"""
    options = Options()
    options.add_argument("--disable-xss-auditor")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-webgl")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--headless")
    return options


def scroll_page(driver: webdriver):
    """Scroll down to bottom of webpage"""
    total_height = int(driver.execute_script(
        "return document.body.scrollHeight"))
    for i in range(1, total_height, 5):
        driver.execute_script("window.scrollTo(0, {});".format(i))


def accept_daft_cookies(driver: webdriver):
    """Click accept cookies"""
    elem = driver.find_element_by_xpath(
        "//*[@class='cc-modal__btn cc-modal__btn--daft']")
    elem.click()


def get_soup_dynamic(url: str, browser_options: Options) -> BeautifulSoup:
    """Get contents of a dynamic webpage and return as a BeautifulSoup object"""
    with webdriver.Chrome(options=browser_options) as driver:
        try:
            driver.get(url)
            # driver.implicitly_wait(5)
            accept_daft_cookies(driver)
            scroll_page(driver)
            soup = BeautifulSoup(driver.page_source, features="lxml")
        except WebDriverException:
            print(url)
            soup = None
    return soup


def get_soup_static(url: str) -> Union[BeautifulSoup, None]:
    try:
        resp = requests.get(url)
        soup = BeautifulSoup(resp.content, features="lxml") if resp.status_code == 200 else None
    except requests.exceptions.ConnectionError as e:
        print(e, "-static-", url)
        soup = None
    return soup


def get_num_listings(soup: BeautifulSoup) -> int:
    """Retrieve the number of listings on Daft"""
    nums = []
    pg_results = soup.find(
        "p", 
        attrs={"class": re.compile("^SearchPagePagination__PaginationResults.*")
    })
    for d in pg_results.text.split(" "):
        try:
            d = int(d.replace(",", ""))
            nums.append(int(d))
        except ValueError:
            continue
    return max(nums)


def get_ber(listing) -> Union[str, None]:
    """Get property BER rating"""
    try:
        ber = re.sub(
            r".+(([ABCDEFG]\d?)|(SI_666))\.svg", 
            r"\1", 
            listing.find("img", attrs={"class": re.compile("^TitleBlock__Ber.*")})["src"])
    except TypeError:
        ber=None
    return ber


def get_href(listing) -> str:
    """Get URL for property"""
    return f"https://www.daft.ie{listing.find(href=True)['href']}"


def get_address(listing) -> str:
    """Get property address"""
    return listing.find(
        "p", 
        attrs={"class": re.compile("^TitleBlock__Address.*")}).text


def get_price(listing) -> int:
    """Get property price"""
    price = listing.find(
        "span", 
        attrs={
            "class": re.compile("^TitleBlock__StyledSpan.*")}).text.strip()
    return int(re.sub("\W", "", price))


def get_agent(listing) -> str:
    try:
        agent = listing.find(
            "span", 
            attrs={
                "class": re.compile("^TitleBlock__AgentNameTextWrapper.*")}).text.strip()
    except AttributeError:
        agent = None
    return agent

def get_other_info(listing):
    """Get remaining info i.e. number of beds, bathrooms and floor size"""
    info_items = listing.find_all(
        "p", 
        attrs={"class": re.compile("^TitleBlock__CardInfoItem.*")})
    for info in info_items:
        yield info["data-testid"], info.text



def get_geolocation(soup: BeautifulSoup) -> tuple:
    if soup is not None:
        try:
            lng, lat = re.findall(r"\[(-[67]{1}\.\d+,5[23]{1}\.\d+)]", str(soup))[0].split(",")
            return float(lng), float(lat)
        except IndexError:
            try:
                lat, lng = re.findall(r"5[23]{1}\.\d+\+-[67]{1}\.\d+", str(soup))[0].split("+")
                return float(lng), float(lat)
            except IndexError:
                return None, None
    else:
        return None, None


def get_stats(soup: BeautifulSoup) -> str:
    stats = soup.find_all(
        "p", 
        attrs={"class": re.compile("^Statistics__StyledLabel.*")})
    date = datetime.strptime(stats[0].text, "%d/%m/%Y")
    views = int(stats[1].text.replace(",", ""))
    return date, views


def scrape_property_page(url: str) -> tuple:
    soup = get_soup_static(url)
    sleep(2)
    if soup is not None:
        try:
            desc = soup.find(
                "div", 
                attrs={"class": re.compile("^PropertyPage__StandardParagraph.*")}).text
        except AttributeError as e:
            print(e, "-function:desc-", url)
            desc = None
        try:
            features = ". ".join([item.text for item in soup.find_all(
                "li", 
                attrs={"class": re.compile("^PropertyDetailsList__PropertyDetailsListItem.*")})])
        except AttributeError as e:
            print(e, "-function:features-", url)
            features = None
        try:
            date, views = get_stats(soup)
        except IndexError as e:
            print(e, "-function:get_stats-", url)
            date, views = None, None
        try:
            lng, lat = get_geolocation(soup)
        except Exception as e:
            print(e, "-function:get_geolocation-", url)
            lng, lat = None, None
        return date, views, desc, features, lng, lat
    else:
        return None, None, None, None, None, None 


def scrape_property_card(listing) -> dict:
    """Scrape Daft property listing information"""
    prop_info = dict(
        href=get_href(listing),
        address=get_address(listing),
        price=get_price(listing),
        ber=get_ber(listing),
        agent=get_agent(listing))
    for info_cls, info in get_other_info(listing):
        prop_info[info_cls] = info
    return prop_info


def scrape_listings(soup: BeautifulSoup):
    """Scrap listings on daft page"""
    listings = soup.find_all(
        "li", 
        attrs={"class": re.compile("^SearchPage__Result.*")})
    for listing in listings:
        try:
            yield scrape_property_card(listing)
        except ValueError:
            continue


def format_df(df: pd.DataFrame):
    df.loc[df["beds"].notna(), "beds"] = (
        df.loc[df["beds"].notna(), "beds"]
            .str.replace(" Bed", "")
            .astype(int))
    df.loc[df["baths"].notna(), "baths"] = (
        df.loc[df["baths"].notna(), "baths"]
            .str.replace(" Bath", "")
            .astype(int))
    na_filter = df["floor-area"].notna()
    df["floor-area-metric"] = np.where(df["floor-area"].str.contains("ac"), "ac", "m2")
    df.loc[na_filter, "floor-area"] = (
        df.loc[na_filter, "floor-area"]
            .str.replace(r" (m²|ac)", "", regex=True)
            .astype(float))
    df["sold"] = 0  # add binary indicator i.e. 0 not sold, 1 sold


def construct_url(
    locations: Union[Iterable, None], 
    price_from: Union[int, None], 
    price_to: Union[int, None], 
    min_beds: Union[str, None]) -> str:
    """"""
    url = "https://www.daft.ie/property-for-sale/ireland/houses?sort=publishDateDesc&from=0&pageSize=20"
    if locations is not None:
        for location in locations:
            url = f"{url}&location={location}"
    if price_from is not None:
        url = f"{url}&salePrice_from={price_from}"
    if price_to is not None:
        url = f"{url}&salePrice_to={price_to}"
    if min_beds is not None:
        url = f"{url}&numBeds_from={min_beds}"
    return url

def scrape_listing_pages(
    locations: Union[Iterable, None], 
    price_from: Union[int, None], 
    price_to: Union[int, None], 
    min_beds: Union[str, None]) -> pd.DataFrame:
    url = construct_url(locations, price_from, price_to, min_beds)
    soup = get_soup_dynamic(url, browser_options=browser_options())
    property_listings = [listing for listing in scrape_listings(soup)]
    pg_sz = 20
    num_pages = ceil(get_num_listings(soup) / pg_sz)
    for i in tqdm(range(1, num_pages)):
        url = re.sub(
            r"(.+)(&from=\d+)(&pageSize=20)", r"\1" + f"&from={i*pg_sz}" + r"\3", url)
        soup = get_soup_dynamic(url, browser_options=browser_options())
        if soup is not None:
            property_listings.extend([listing for listing in scrape_listings(soup)])
        # sleep(2)
    # Create dataframe of property listings
    df = pd.DataFrame(property_listings).drop_duplicates(subset=["address", "price"])
    format_df(df)
    return df


def scrape_daft_for_sale(
    locations: Union[Iterable, None]=None, 
    price_from: Union[int, None]=None, 
    price_to: Union[int, None]=None, 
    min_beds: Union[str, None]=None, 
    df_old: Union[pd.DataFrame, None]=None) -> pd.DataFrame:
    """Scrape all property sale listings on Daft"""
    df_new = scrape_listing_pages(locations, price_from, price_to, min_beds)
    if df_old is not None:
        # check if listings were sold and assign 1 if sold
        df_old.loc[df_old["href"].isin(set(df_old["href"]).difference(df_new["href"])), "sold"] = 1
        # subset of new listing
        df_new = df_new.loc[df_new["href"].isin(set(df_new["href"]).difference(df_old["href"]))]
    df_new["date_posted"], df_new["views"], df_new["desc"], df_new["features"], df_new["lng"], df_new["lat"] = zip(
        *df_new["href"].apply(scrape_property_page))
    df_new["date_scraped"] = datetime.now()
    df_new["date_scraped"] = pd.to_datetime(df_new["date_scraped"])
    df_new["date_posted"] = pd.to_datetime(df_new["date_posted"])
    return df_new
