# Property Data

The purpose of this repo is to create a dataset used for a web application, which performs an analysis of the property market for Dublin and the commuter counties of Kildare, Meath and Wicklow.

## Setup

* Virtualenv

```bash
$ pip install -r requirements.txt
```

* Pipenv

```bash
$ pipenv shell
```

## Command Line

To retrieve property for sale information, `create_dataset.py` script is used with the following arguments:

* --filename / -f: filepath to save information. Note that if information was previously saved. Specifying this path will append new information.
* --locations / -l: locations to scrape information for. Default locations are Dublin, Meath, Kildare and Wicklow
* --price_from: Lower bound of price range to scrape information for. Default value is 0.
* --price_to: Upper bound of price range to scrape information for. Default value is 10000000.
* --beds: Lower bound of number of beds range to scrape information for. Default value is 2.

Example:

```bash
$ python create_dataset.py -f rough_work/data/test_4.tsv -l dublin meath kildare wicklow --price_from 0 --price_to 10000000 --beds 2
```
