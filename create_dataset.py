from housing import scrape_daft_for_sale, get_location_info
import argparse
import pandas as pd
import urllib


def get_args():
    """Function to parse input arguments"""
    parser = argparse.ArgumentParser(description="Scrape property information")
    parser.add_argument("-f", "--filename", required=True, help="""
        Filepath or URL to save data to and / or where previously scraped data
        is stored.
    """)
    parser.add_argument("-l", "--locations", nargs="+", help="""
        Specify a list of county locations.
    """, default=None)
    parser.add_argument("--price_from", type=int, help="""
        Specify lower price bound.
    """, default=None)
    parser.add_argument("--price_to", type=int, help="""
        Specify upper price bound.
    """, default=None)
    parser.add_argument("--beds", type=int, help="""
        Specify lower bound of number of beds.
    """, default=None)
    return parser.parse_args()


def classify_estate_agents(df):
    estate_agents = [
        "Ray Cooke Auctioneers", "DNG", "Sherry FitzGerald", "Flynn & Associates Ltd", 
        "Lisney", "Quillsen" ,"REA", "Hunters Estate Agent", "Ray Cooke Auctioneers", "Keller Williams",
        "PropertyTeam", "RE/MAX", "Murphy Mullan", "Mason Estates", "Savills", "Property Partners"
    ]
    df["estate_agent"] = None
    df.loc[df["agent"].isna(), "agent"] = ""
    for estate_agent in estate_agents:
        df.loc[df["agent"].str.contains(estate_agent), "estate_agent"] = estate_agent
    df.loc[df["estate_agent"].isna(), "estate_agent"] = df.loc[df["estate_agent"].isna(), "agent"]
    df.drop("agent", axis=1, inplace=True)


def main():
    args = get_args()
    try:
        df_old = pd.read_csv(args.filename, "\t", index_col=0)
        df_new = scrape_daft_for_sale(
            locations=args.locations, 
            price_from=args.price_from, 
            price_to=args.price_to, 
            min_beds=args.beds, 
            df_old=df_old)
        get_location_info(df_new)
        classify_estate_agents(df_new)
        df_new = pd.concat([df_old, df_new]).reset_index(drop=True)
    except (FileNotFoundError, urllib.request.HTTPError):
        df_new = scrape_daft_for_sale(
            locations=args.locations, 
            price_from=args.price_from, 
            price_to=args.price_to, 
            min_beds=args.beds)
        get_location_info(df_new)
    df_new.to_csv(args.filename, "\t")


if __name__ == "__main__":
    main()