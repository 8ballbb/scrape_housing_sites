# Property Data

The purpose of this repo is to scrape property market data for Dublin and the commuter counties of Kildare, Meath and Wicklow.

## Setup

* Pipenv

```bash
pipenv shell
```

## Usage

* Scrape data

```bash
python create_dataset.py
```

* Scrape data and append to existing data

```bash
python create_dataset.py -d {data.tsv}
```
