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

    def calculator(self, stock_data, period, fn):
        """
        시작은 순수 python 계산으로 하자.
        """
        LOGGER.info('calculator...')
        result = None
        try:
            if (fn.upper() == 'SMA'):
                result = self.cal_SMA(stock_data, period)
            else:
                LOGGER.info('Not currected site!!')
        except Exception as e:
            LOGGER.info(e)
        return result

    def cal_SMA(self, data, period):
        """
        이 기능은 최초 발행일부터 오늘까지 데이터가 있다고 가정하고
        SMA를 구할 수 있는 함수로 작성하기
        """
        LOGGER.info('cal_SMA...')
        try:
            dates = list(data.keys())
            dates.sort()
            average_dict = {}
            LOGGER.info('dates length: {}'.format(len(dates)))

            for index, date in enumerate(dates):
                index += 1
                # period = period - 1  # incloud today..
                period_dates = [day for day in dates[(
                    index-period):index] if index >= period]
                total = sum(float(data[date]['Close'])
                            for date in period_dates)
                SMA = total / int(period)
                average_dict[date] = SMA
                # LOGGER.info('count: {}, date: {}, SMA:{}, curr:{}'.format(index, date, SMA, data[date]['Close']))

        except Exception as e:
            LOGGER.info('[ERROR] cal_SMA: {}'.format(e))
        return self._filter_invild_MA(average_dict)

    def _filter_invild_MA(self, data):
        LOGGER.info('_filter_invild_MA...')
        try:
            build_data = {}
            for key, value in data.items():
                if value != 0:
                    build_data[key] = value
        except Exception as e:
            LOGGER.info('[ERROR] _filter_invild_MA: {}'.format(e))
        return build_data


if __name__ == '__main__':
    init_logging()

    # Required
    # python3 calculator.py --ticker qqq --days 200 --fn sma
    parser = argparse.ArgumentParser()
    parser.add_argument('--ticker', required=True)
    parser.add_argument('--period', required=True)
    parser.add_argument('--fn', required=False)
    args = parser.parse_args()

    ticker = ('ticker' in args) and args.ticker or None
    period = ('period' in args) and int(args.period) or 10
    fn = ('fn' in args) and args.fn or 'sma'

    # step 1. read list of urls
    with open('./csv/{}.json'.format(ticker), 'r', errors='surrogatepass') as f:
        stock_data = json.load(f)

    # instance class
    myCal = Calculator()

    # fetch data
    data = myCal.calculator(
        stock_data=stock_data,
        period=period,
        fn=fn)

    LOGGER.info('data: {}'.format(data))

    with open('./csv/{}_graph.json'.format(ticker), 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
