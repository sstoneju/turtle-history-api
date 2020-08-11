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


class Downloader(object):
    def __init__(self):
        LOGGER.info('Init Downloader...')

    def fetchh_etf_dict(self, ticker, days, contry, site):
        """
        https://stooq.com/q/d/l/?s=qqq.us&i=d
        https://query1.finance.yahoo.com/v7/finance/download/TQQQ?period1=0&period2=1597017600&interval=1d&events=history
        https://api.nasdaq.com/api/quote/SPY/info?assetclass=etf
        https://www.nasdaq.com/api/v1/historical/SPY/etf/2010-08-10/2020-08-10

        이곳에서 데이터를 받아온다. SHY, QQQ BND, AGG, VWO를 기본적으로 돌릴 수 있게 한다.
        """
        LOGGER.info('>> fetchh_etf_history: {}, {}, {}'.format(
            ticker, contry, site))

        try:
            target_url = ''
            history = {}

            target_url = self._build_download_url(
                ticker=ticker,
                days=days,
                site=site,
                contry=contry)

            with closing(requests.get(target_url, stream=True)) as r:
                f = (line.decode('utf-8') for line in r.iter_lines())
                reader = csv.DictReader(f, delimiter=',', quotechar='"')

                for row in reader:
                    key = row.pop('Date')
                    if key in history:
                        # implement your duplicate row handling here
                        pass
                    history[key] = self._to_dict(row)
        except Exception as e:
            LOGGER.info(e)
        return history

    def fetchh_etf_np(self, ticker, days, contry, site):
        """
        제대로 테스트 안했음..
        """
        LOGGER.info('>> fetchh_etf_np: {}, {}, {}'.format(
            ticker, contry, site))
        try:
            import numpy as np

            target_url = ''
            history = None

            target_url = self._build_download_url(
                ticker=ticker,
                days=days,
                site=site,
                contry=contry)

            with closing(requests.get(target_url, stream=True)) as r:
                f = (line.decode('utf-8') for line in r.iter_lines())
                reader = csv.reader(f, delimiter=',', quotechar='"')
                history = np.array(reader)
        except Exception as e:
            LOGGER.info(e)
        return history

    def _to_dict(self, input_ordered_dict):
        return json.loads(json.dumps(input_ordered_dict))

    def fetch_etf_ticker(self, top=20):
        """
        https://api.nasdaq.com/api/screener/etf?tableonly=true&limit=20
        """
        return

    def _build_download_url(self, ticker, days, site, contry):
        LOGGER.info('>> _build_download_url')
        today = datetime.now()
        LOGGER.info('curr_timestamp: {}'.format(today))

        if int(days % WEEK) >= 1:
            days += (int(days / WEEK) + 5)  # 토, 일해서 2일이 맞지만 여유일로 더 넣음.

        try:
            if site.upper() == 'YAHOO':
                """
                period1=0&period2=1597017600&interval=1d&events=history

                current time == deploy country time
                """
                period1 = today - timedelta(days=days)
                payload = {'period1': int(period1.timestamp()), 'period2': int(today.timestamp()),
                           'interval': '1d', 'events': 'history'}
                base_url = "https://query1.finance.yahoo.com/v7/finance/download/{}?".format(
                    ticker.upper())
                LOGGER.info('base_url: {}'.format(base_url))
                query_string = urlencode(payload)
                LOGGER.info('query_string: {}'.format(query_string))
                base_url += query_string
                LOGGER.info('bind_url: {}'.format(base_url))
            else:
                LOGGER.info('Not currected site!!')
        except Exception as e:
            LOGGER.info(e)
        return base_url


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
    data = myDownloader.fetchh_etf_dict(
        ticker=ticker,
        days=days,
        contry=default_contry,
        site=default_site)

    with open('./csv/{}.json'.format(ticker), 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    # LOGGER.info('data: {}'.format(data))
