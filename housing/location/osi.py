from typing import Union, Iterable
from functools import partial
import geopandas as gpd


def get_location_info(df):
    df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["lng"], df["lat"]))
    df_small_area = get_small_area_data()
    df_constituency = get_constituency_data()
    df_electoral = get_electoral_data()
    df_local_electoral = get_local_electoral_data()
    osi_info = partial(
        get_osi_info, 
        df_small_area=df_small_area, 
        df_constituency=df_constituency, 
        df_electoral=df_electoral, 
        df_local_electoral=df_local_electoral)
    df["county_name"], df["small_area"], df["constituency"], df["province"], df["local_electoral"], df["county"] = zip(
        *df["geometry"].apply(osi_info))
    return df


def get_osi_info(
    point,
    df_small_area: gpd.geodataframe.GeoDataFrame, 
    df_constituency: gpd.geodataframe.GeoDataFrame, 
    df_electoral: gpd.geodataframe.GeoDataFrame, 
    df_local_electoral: gpd.geodataframe.GeoDataFrame):
    county_area, area = get_small_area_info(df_small_area, point)
    constituency = get_constituency_info(df_constituency, point)
    _, province = get_electoral_info(df_electoral, point)
    electoral_local, county = get_local_electoral_info(df_local_electoral, point)
    return county_area, area, constituency, province, electoral_local, county


def get_small_area_info(
    df_small_area: gpd.geodataframe.GeoDataFrame, point) -> Iterable:
    """TODO: Refactor required"""
    small_area_filter = df_small_area["geometry"].contains(point)
    small_areas = df_small_area.loc[small_area_filter]
    if len(small_areas) > 1 or len(small_areas) == 0:
        area, county_area = None, None
    else:
        area = small_areas["EDNAME"].iloc[0]
        county_area = small_areas["COUNTYNAME"].iloc[0]
    return county_area, area


def get_constituency_info(
    df_constituency: gpd.geodataframe.GeoDataFrame, point) -> Union[str, None]:
    """TODO: Refactor required"""
    constituency_filter = df_constituency["geometry"].contains(point)
    constituencies = df_constituency.loc[constituency_filter]
    if len(constituencies) > 1 or len(constituencies) == 0:
        constituency = None
    else:
        constituency = constituencies["constituency"].iloc[0]
    return constituency


def get_electoral_info(
    df_electoral: gpd.geodataframe.GeoDataFrame, point) -> Union[str, None]:
    """TODO: Refactor required"""
    electoral_filter = df_electoral["geometry"].contains(point)
    electoral_divisions = df_electoral.loc[electoral_filter]
    if len(electoral_divisions) > 1 or len(electoral_divisions) == 0:
        electoral_div, province = None, None
    else:
        electoral_div = electoral_divisions["CSOED_34_1"].iloc[0]
        province = electoral_divisions["PROVINCE"].iloc[0]
    return electoral_div, province


def get_local_electoral_info(df_local_electoral: gpd.geodataframe.GeoDataFrame, point) -> Union[str, None]:
    """TODO: Refactor required"""
    electoral_filter = df_local_electoral["geometry"].contains(point)
    local_electorals = df_local_electoral.loc[electoral_filter]
    if len(local_electorals) > 1 or len(local_electorals) == 0:
        electoral_local, county = None, None
    else:
        electoral_local = local_electorals["local_electoral"].iloc[0]
        county = local_electorals["COUNTY"].iloc[0]
    return electoral_local, county


def get_small_area_data() -> gpd.geodataframe.GeoDataFrame:
    """TODO: write docstring"""
    shp_data = "data/Small_Areas_Ungeneralised_-_OSi_National_Statistical_Boundaries_-_2015-shp/"
    df_small_area = gpd.read_file(shp_data)
    df_small_area = df_small_area.loc[:, ["COUNTYNAME", "EDNAME", "geometry"]]
    df_small_area = df_small_area.to_crs(epsg=4326)
    return df_small_area


def get_constituency_data() -> gpd.geodataframe.GeoDataFrame:
    """TODO: write docstring"""
    shp_data = "data/Constituency_Boundaries_Ungeneralised_-_OSi_National_Electoral_Boundaries_-_2017/"
    df_constituency = gpd.read_file(shp_data)
    df_constituency = df_constituency.to_crs(epsg=4326)
    df_constituency["constituency"] = df_constituency["CON_SEAT_"].str.replace(r"(.+) \(\d\)", r"\1", regex=True)
    df_constituency = df_constituency.loc[:, ["constituency", "geometry"]]
    return df_constituency


def get_electoral_data() -> gpd.geodataframe.GeoDataFrame:
    """TODO: write docstring"""
    shp_data = "data/CSO_Electoral_Divisions_Ungeneralised_-_OSi_National_Statistical_Boundaries_-_2015-shp/"
    df_electoral = gpd.read_file(shp_data)
    df_electoral = df_electoral.to_crs(epsg=4326)
    df_electoral = df_electoral.loc[:, ["CSOED_34_1", "PROVINCE", "geometry"]]
    return df_electoral


def get_local_electoral_data() -> gpd.geodataframe.GeoDataFrame:
    """TODO: write docstring"""
    shp_data = "data/Local_Electoral_Areas_-_OSi_National_Statutory_Boundaries-shp/"
    df_local_electoral = gpd.read_file(shp_data)
    df_local_electoral = df_local_electoral.to_crs(epsg=4326)
    df_local_electoral = df_local_electoral.loc[:, ["COUNTY", "ENGLISH", "geometry"]]
    df_local_electoral["local_electoral"] = (df_local_electoral["ENGLISH"]
                                                 .str.replace(r"( LEA-\d|-LEA-\d)", "", regex=True)
                                                 .str.title())
    df_local_electoral["COUNTY"] = df_local_electoral["COUNTY"].str.title()
    return df_local_electoral
