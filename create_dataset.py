from scrapers.daft import scrape_daft_for_sale
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
        Specify a list of county locations. Default counties are Dublin, Meath,
        Kildare and Wicklow.
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


def main():
    args = get_args()
    try:
        df_old = pd.read_csv(args.filename, "\t", index_col=0)
        df = scrape_daft_for_sale(
            locations=args.locations, 
            price_from=args.price_from, 
            price_to=args.price_to, 
            min_beds=args.beds, 
            df=df_old)
    except (FileNotFoundError, urllib.request.HTTPError):
        df = scrape_daft_for_sale(
            locations=args.locations, 
            price_from=args.price_from, 
            price_to=args.price_to, 
            min_beds=args.beds)
    df.to_csv(args.filename, "\t")


if __name__ == "__main__":
    main()
