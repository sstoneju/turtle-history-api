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

    def calculator(self, stock_data, days, fn):
        """
        시작은 순수 python 계산으로 하자.
        """
        LOGGER.info('calculator...')
        result = None
        try:
            if (fn.upper() == 'SMA'):
                result = self.cal_SMA(stock_data, days)
            else:
                LOGGER.info('Not currected site!!')
        except Exception as e:
            LOGGER.info(e)
        return result

    def cal_SMA(self, prices, period):
        LOGGER.info('cal_SMA...')
        try:
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
        except Exception as e:
            LOGGER.info(e)
        return average_dict


if __name__ == '__main__':
    init_logging()

    # Required
    # python3 calculator.py --ticker qqq --days 200 --fn sma
    parser = argparse.ArgumentParser()
    parser.add_argument('--ticker', required=True)
    parser.add_argument('--days', required=True)
    parser.add_argument('--fn', required=False)
    args = parser.parse_args()

    ticker = 'ticker' in args and args.ticker or None
    days = 'days' in args and int(args.days) or 10
    fn = 'fn' in args and args.fn or 'sma'

    # step 1. read list of urls
    with open('./csv/{}.json'.format(ticker), 'r', errors='surrogatepass') as f:
        stock_data = json.load(f)

    # instance class
    myCal = Calculator()

    # fetch data
    data = myCal.calculator(
        stock_data=stock_data,
        days=days,
        fn=fn)

    LOGGER.info('data: {}'.format(data))
