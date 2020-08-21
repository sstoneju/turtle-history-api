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

from chalice import Chalice
from msg_maker import MsgMaker
from alarm_service import alarm_to_slack

app = Chalice(app_name='StockAlarm')


@app.route('/')
def index():
    return app.current_request.to_dict()


@app.route('/alarm', methods=['GET'])
def alarm_tickers():
    '''
    us-east-1 시간이 적용된다. 하루의 장이 마감이 되면
    tickerList 읽어서 Slack으로 알람을 쏴준다.
    '''
    ticker_str = os.environ['tickerList']  # `{"AGG":200,"BND":200}`
    ticker_list = json.loads(ticker_str)

    msg_maker = MsgMaker()

    for key, value in ticker_list.items():
        bind_content = msg_maker.make_today_MA(key, value)
        alarm_to_slack(bind_content)

    return {'result': 'success'}
