# -*- coding: utf-8 -*-
from chalice import Chalice

import sys
import json
import logging
import os
import time
from datetime import date, datetime, timedelta


app = Chalice(app_name='turtle-history-api')

@app.route('/')
def index():
    return {'hello': 'world'}


@app.route('/meta')
def call_meta():
    return app.current_request.to_dict()


@app.route('/history/{ticker}', methods=['GET'])
def history_tickers(ticker=None):
    from chalicelib.downloader import Downloader

    '''
    ticker를 받아서 history를 보여준다.
    https://aws.github.io/chalice/tutorials/basicrestapi.html 사용법

    start_date=20010505
    end_date=20201010
    '''

    if ticker is None:
        return {'error':'Ticker is None...'}

    today = datetime.now()
    params = app.current_request.query_params if app.current_request.query_params else {}

    start_date = convert_string_to_date(str(params['start'])) if 'start' in params else today - timedelta(weeks=52)
    end_date = convert_string_to_date(params['end']) if 'end' in params else today

    downloader =  Downloader()
    histries = downloader.fetchh_etf_dict(ticker=ticker, start_date=start_date, end_date=end_date)

    return {'result': 'success', 'list':histries}

def convert_string_to_date(str_date:str, form='%Y%m%d'):
    str_date = ''.join(str_date.split('.')) if str_date.split('.') else str_date
    str_date = ''.join(str_date.split('-')) if str_date.split('-') else str_date
    str_date = ''.join(str_date.split('/')) if str_date.split('/') else str_date
    date_obj = datetime.strptime(str_date, form)
    return date_obj

@app.route('/alarm', methods=['GET'])
def alarm_tickers():
    from chalicelib.msg_maker import MsgMaker
    from chalicelib.alarm_service import alarm_to_slack
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


@app.schedule('cron(30 4 * * ? 1-5)')
def schedule_tickers():
    from chalicelib.msg_maker import MsgMaker
    from chalicelib.alarm_service import alarm_to_slack
    '''
    cron(min > hour > day(일) > month > weekday(요일))
    '''
    ticker_str = os.environ['tickerList']  # `{"AGG":200,"BND":200}`
    ticker_list = json.loads(ticker_str)

    msg_maker = MsgMaker()

    for key, value in ticker_list.items():
        bind_content = msg_maker.make_today_MA(key, value)
        alarm_to_slack(bind_content)

    return {'result': 'success'}
