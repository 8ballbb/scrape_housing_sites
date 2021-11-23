from .listings import scrape_listing_pages
from .properties import scrape_property_page
from .osi import get_location_info
from datetime import datetime
from typing import Union
import pandas as pd


def get_new_listings(headers: dict, df_old_listings: Union[pd.DataFrame, None]=None) -> pd.DataFrame:
    data, live_listing_addresses = [], []
    for listing in scrape_listing_pages(headers):
        live_listing_addresses.append(listing["address"])
        if df_old_listings is None or df_old_listings["url"].str.contains(listing["url"]).sum() == 0:
            # scrape new listing
            listing["view_count"], listing["description"], listing["features"] = scrape_property_page(
                headers, listing["url"])
            listing["currently_listed"] = 1
            data.append(listing)
        else:
            # data scraped already
            continue
    if df_old_listings is not None:  # reset currently_listed indicator
        df_old_listings.loc[
            ~df_old_listings["address"].isin(live_listing_addresses), "currently_listed"] = 0
    print(f"\n{len(data)} new house listings\n")
    df_new_listings = pd.DataFrame(data)
    df_new_listings["currently_listed"] = 1
    return df_new_listings


def scrape_daft(headers: dict, df_old_listings: Union[pd.DataFrame, None]) -> pd.DataFrame:
    """Scrape all property sale listings on Daft"""
    # Get new listings
    df_new_listings = get_new_listings(headers, df_old_listings)
    get_location_info(df_new_listings)  # get location data for new listings
    df_listings = pd.concat([df_new_listings, df_old_listings]).reset_index(drop=True)
    return df_listings
