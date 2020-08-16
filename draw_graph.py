
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
import matplotlib.pyplot as plt
import numpy as np


LOGGER = logging.getLogger()


def init_logging():
    LOGGER.setLevel(logging.INFO)
    fmt = logging.Formatter('%(asctime)s: %(message)s', '%m/%d/%Y %I:%M:%S %p')
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    LOGGER.addHandler(console)


def draw_sma(data):
    build_data = []
    for key, value in data.items():
        build_data.append(value)
    title = [val for val in data]
    LOGGER.info('title_data: {}'.format(title))
    LOGGER.info('extract_data: {}'.format(build_data))
    parse_log = np.log(build_data)
    plt.plot(parse_log)
    plt.show()
    return


if __name__ == '__main__':
    init_logging()

    # Required
    # python3 calculator.py --ticker qqq --days 200 --fn sma
    parser = argparse.ArgumentParser()
    parser.add_argument('--ticker', required=True)
    args = parser.parse_args()

    ticker = ('ticker' in args) and args.ticker or None

    # step 1. read list of urls
    with open('./csv/{}_graph.json'.format(ticker), 'r', errors='surrogatepass') as f:
        stock_data = json.load(f)

    draw_sma(stock_data)
    # # instance class
    # myCal = Calculator()

    # # fetch data
    # data = myCal.calculator(
    #     stock_data=stock_data,
    #     period=period,
    #     fn=fn)

    # LOGGER.info('data: {}'.format(data))
