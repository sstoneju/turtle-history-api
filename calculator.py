# -*- coding: utf-8 -*-

import sys
import argparse
import json
import logging
import os
import time
from urllib.parse import urlencode
import re
import requests
import csv
from contextlib import closing
from datetime import datetime, timedelta

# import pandas as pd
# import pdb
# import glob
# from tqdm import tqdm

# GLOBAL
LOGGER = logging.getLogger()
WEEK = 7


def init_logging():
    LOGGER.setLevel(logging.INFO)
    fmt = logging.Formatter('%(asctime)s: %(message)s', '%m/%d/%Y %I:%M:%S %p')
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    LOGGER.addHandler(console)


class Calculator(object):
    def __init__(self):
        LOGGER.info('Init Calculator...')

    def calculateMovingAverage(self, prices, period):
        dates = list(prices.keys())
        dates.sort()
        total = 0.0
        count = 0
        average_dict = {}
        LOGGER.info(dates)

        for i, d in enumerate(dates):
            # search through prior dates and eliminate any that are too old
            old = [e for e in dates[i-count:i] if (d-e).days > period]
            total -= sum(prices[o] for o in old)
            count -= len(old)

            # add in the current date
            total += prices[d]
            count += 1

            average_dict[d] = total / count

        return average_dict


if __name__ == '__main__':
    init_logging()

    # Required
    parser = argparse.ArgumentParser()
    parser.add_argument('--ticker', required=True)
    parser.add_argument('--days', required=True)
    parser.add_argument('--default_contry', required=False)
    parser.add_argument('--default_site', required=False)
    args = parser.parse_args()

    ticker = 'ticker' in args and args.ticker or None
    days = 'days' in args and int(args.days) or 10
    default_contry = 'default_contry' in args and args.default_contry or 'us'
    default_site = 'default_site' in args and args.default_site or 'yahoo'

    # instance class
    myDownloader = Downloader()

    # fetch data
    data = myDownloader.fetchh_etf_history(
        ticker=ticker,
        days=days,
        contry=default_contry,
        site=default_site)

    LOGGER.info('data: {}'.format(data))
