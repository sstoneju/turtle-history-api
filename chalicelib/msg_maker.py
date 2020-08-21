# -*- coding: utf-8 -*-

import sys
import argparse
import json
import logging
import os
import time
from urllib.parse import urlencode
import re
import csv
from datetime import datetime, timedelta
from .downloader import Downloader
from .calculator import Calculator

# GLOBAL
LOGGER = logging.getLogger()


def init_logging():
    LOGGER.setLevel(logging.INFO)
    fmt = logging.Formatter('%(asctime)s: %(message)s', '%m/%d/%Y %I:%M:%S %p')
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    LOGGER.addHandler(console)


class MsgMaker(object):
    def __init__(self):
        LOGGER.info('Init Service...')
        self.fetcher = Downloader()
        self.calculator = Calculator()

    def make_today_MA(self, ticker, period):
        """
        ex) {ticker}에 대한 {period}를 정해준대로, 오늘의 MA과 비교해서 매도 타이밍을 알려준다. -> 알람 메시지 작성
        """
        # period에 해당하는 데이터를 가지고 온다.
        histories = self.fetcher.fetchh_etf_dict(ticker=ticker, period=period)

        date = list(histories.keys())
        date.sort()
        last_day = date[-1]
        LOGGER.info('started_day: {}'.format(date[0]))
        lastest_info = histories[last_day]  # 최근의 종가 가격
        LOGGER.info('lastest_info: {}'.format(lastest_info))

        cal_list = self.calculator.calculate(histories, period, fn='SMA')
        today_Ma = cal_list[last_day]

        flag = 'to Keep' if today_Ma <= float(
            lastest_info['Close']) else 'to Sell'

        return {
            'pretext': 'Alarm for MA{}'.format(period),
            'text': 'Ticker: {} \nClose: {} \nMA{}: {} \n*Let us {} shares*'.format(
                ticker.upper(),
                lastest_info['Close'][0:-2],
                period,
                round(float(today_Ma), 4),
                flag),
        }


if __name__ == '__main__':
    init_logging()

    # Required
    parser = argparse.ArgumentParser()
    parser.add_argument('--ticker', required=True)
    parser.add_argument('--period', required=True)
    args = parser.parse_args()

    ticker = 'ticker' in args and args.ticker or None
    period = 'period' in args and int(args.period) or 180  # default 6 month

    maker = MsgMaker()
    alarm_msg = maker.make_today_MA(ticker, period)

    LOGGER.info('alarm_msg: {}'.format(alarm_msg))
