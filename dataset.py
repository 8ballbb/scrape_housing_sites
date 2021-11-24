from housing import scrape_daft
from glob import glob
from datetime import datetime
import os
from fake_useragent import UserAgent
import pandas as pd


def main():
    headers = {
        "authority": "gateway.daft.ie",
        "sec-ch-ua": "'Chromium';v='94', 'Google Chrome';v='94', ';Not A Brand';v='99'",
        "pragma": "no-cache",
        "dnt": "1",
        "sec-ch-ua-mobile": "?0",
        "user-agent": UserAgent().chrome,
        "content-type": "application/json",
        "accept": "application/json",
        "cache-control": "no-cache, no-store",
        "brand": "daft",
        "platform": "web",
        "sec-ch-ua-platform": "'macOS'",
        "expires": "0",
        "origin": "https://www.daft.ie",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://www.daft.ie/",
        "accept-language": "en-US,en;q=0.9"
    }
    data_dir = "data"
    if os.path.exists(data_dir):
        latest_file = max(glob(f"{data_dir}/*"), key=os.path.getctime)
        df_old_listings = pd.read_csv(latest_file, sep="\t", index_col=0)  # read previous data scraped
    else:
        df_old_listings = None
    df = scrape_daft(headers, df_old_listings=df_old_listings)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    date = datetime.now().strftime('%Y_%m_%d')
    print(f"\n{len(df)} total listings\n")
    df.to_csv(f"{data_dir}/{date}.tsv", "\t")


if __name__ == "__main__":
    main()
