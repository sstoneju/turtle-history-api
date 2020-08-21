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
from msg_maker import MsgMaker

# GLOBAL
LOGGER = logging.getLogger()


def init_logging():
    LOGGER.setLevel(logging.INFO)
    fmt = logging.Formatter('%(asctime)s: %(message)s', '%m/%d/%Y %I:%M:%S %p')
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    LOGGER.addHandler(console)


def alarm_to_slack(content):
    """
    해당 url(slack)으로 content를 전송한다.
    """
    # period에 해당하는 데이터를 가지고 온다.
    try:
        url = os.environ['alarmUrl'] or ''
        response = requests.post(url, json=content)
        LOGGER.info('{}'.format(response))
    except Exception as e:
        LOGGER.info('{}'.format(e))
    return response


if __name__ == '__main__':
    init_logging()
    url = ''
    content = {'pretext': 'Alarm for MA180',
               'text': 'Ticker: AGG \nClose: 118.3499 \nMA180: 115.8491 \n*Let us to Keep shares*'}
    alarm_to_slack(url, content)
