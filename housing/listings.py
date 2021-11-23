from .utils import error_handler
from datetime import datetime
import json
from time import sleep
import re
import requests
from tqdm import tqdm


PAYLOAD = {
    "section": "residential-for-sale",
    "filters": [
        {
        "name": "adState",
        "values": ["published"]
        },
        {
        "values": ["houses"],
        "name": "propertyType"
        }
    ],
    "andFilters": [],
    "ranges": [],
    "paging": {
        "from": "0",
        "pageSize": "50"
    },
    "geoFilter": {
        "storedShapeIds": ["1", "3", "2", "4"],
        "geoSearchType": "STORED_SHAPES"
    },
    "terms": "",
    "sort": "publishDateDesc"
}


def get_price(listing: dict) -> int:
    """Get property price"""
    try:
        return int(re.sub("\D", "", listing["price"]))
    except ValueError:
        return "POA"


def get_bed(listing: dict) -> int:
    try:
        return int(listing["numBedrooms"].lower().replace(" bed", ""))
    except ValueError:
        if "&" in listing["numBedrooms"]:
            return int(max(
                listing["numBedrooms"].lower().replace(" bed", "").split(" & ")))


def get_bath(listing: dict) -> int:
    return int(listing["numBathrooms"].lower().replace(" bath", ""))


def get_ber(listing: dict) -> str:
    return listing["ber"]["rating"]


def get_floor_area(listing: dict) -> float:
    return float(listing["floorArea"]["value"])


def get_floor_area_unit(listing: dict) -> str:
    return listing["floorArea"]["unit"]


def get_property_type(listing: dict) -> str:
    return listing["propertyType"]


def get_estate_agent(listing: dict) -> str:
    estate_agents = [
        "Ray Cooke Auctioneers", "DNG", "Sherry FitzGerald", 
        "Flynn & Associates Ltd", "Lisney", "Quillsen" ,"REA", 
        "Hunters Estate Agent", "Ray Cooke Auctioneers", 
        "Keller Williams", "PropertyTeam", "RE/MAX", "Murphy Mullan", 
        "Mason Estates", "Savills", "Property Partners"
    ]
    for ea in estate_agents:
        if ea in listing["seller"]["branch"]:
            listing["seller"]["branch"] = ea
            break
    return listing["seller"]["branch"]


def get_lng(listing: dict) -> float:
    return listing["point"]["coordinates"][0]


def get_lat(listing: dict) -> float:
    return listing["point"]["coordinates"][1]


def get_listing_date(listing: dict) -> str:
    """Milliseconds since epoch"""
    try:
        return datetime.fromtimestamp(
            listing["publishData"]/1000).strftime("%Y-%m-%d")
    except KeyError:
        return datetime.now().strftime('%Y-%m-%d')
    

def get_listing_data(listing):
    listing_data = dict(
        daft_id=listing["id"],
        url=f"https://www.daft.ie{listing['seoFriendlyPath']}",
        address=listing["title"],
        price=error_handler(get_price, listing),
        beds=error_handler(get_bed, listing),
        baths=error_handler(get_bath, listing),
        property_type=error_handler(get_property_type, listing),
        estate_agent=error_handler(get_estate_agent, listing),
        ber=error_handler(get_ber, listing),
        floor_area=error_handler(get_floor_area, listing),
        floor_area_unit=error_handler(get_floor_area_unit, listing),
        lng=error_handler(get_lng, listing), 
        lat=error_handler(get_lat, listing),
        publish_date=get_listing_date(listing)
    )
    return listing_data
    

def get_total_pages(headers) -> int:
    """Get number of pages to scrape"""
    response = requests.request(
        "POST", "https://gateway.daft.ie/old/v1/listings", 
        headers=headers, 
        data=json.dumps(PAYLOAD))
    results = json.loads(response.content)
    return results["paging"]["totalPages"]


def scrape_listing_pages(headers: dict) -> list:
    """Scrape data from each listing"""
    total_pages = get_total_pages(headers)  # get number of pages with listings
    for _ in tqdm(range(total_pages)):
        response = requests.request(
            "POST", "https://gateway.daft.ie/old/v1/listings", 
            headers=headers, 
            data=json.dumps(PAYLOAD))
        if response.status_code == 200:
            listings = json.loads(response.content)["listings"]
            for listing in listings:
                yield get_listing_data(listing["listing"])
        # Set page number
        PAYLOAD["paging"]["from"] = (
            int(PAYLOAD["paging"]["from"]) + int(PAYLOAD["paging"]["pageSize"]))
        sleep(2)
