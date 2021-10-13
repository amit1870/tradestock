"""
This script will place order using real time price of stock.
Decision to place order will be done by Bollinger Band strategy.
"""

import websocket
import ssl
import random
import _thread
import time
import json
import argparse
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from requests.exceptions import HTTPError
from datetime import datetime, timedelta
from ibw.client import IBClient
from utils.auto_mode import auto_mode_on_accounts

plt.style.use('fivethirtyeight')
pd.options.mode.chained_assignment = None  # default='warn'

URL = "wss://localhost:5000/v1/api/ws"

SERVER_IDS = []
DATA_FRAMES = []
PERIOD = 3
AUTH_DONE = False
DATA_LIST = []
STD_FACTOR_UPPER = 0.1
STD_FACTOR_LOWER = 0.1

def print_df(data_frames, use_str=True):

    if use_str:
        print(data_frames.to_string())
    else:
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(data_frames)

def bolliner_bands(data_list, period):
    df = pd.DataFrame(data_list)

    # set the date as the index
    df = df.set_index(pd.DatetimeIndex(df['Date'].values))

    # Calculate Simple Moving Average, Std Deviation, Upper Band and Lower Band
    df['SMA'] = df['Close'].rolling(window=period).mean()

    df['STD'] = df['Close'].rolling(window=period).std()

    df['Upper'] = df['SMA'] + (df['STD'] * STD_FACTOR_UPPER)

    df['Lower'] = df['SMA'] - (df['STD'] * STD_FACTOR_LOWER)

    # create a new data frame
    new_df = df[period-1:]

    return new_df


def update_data(data, start_date_str):
    """ Add Date to each item of list."""
    start_date_j = datetime.strptime(start_date_str, '%Y%m%d-%H:%M:%S')
    start_date = start_date_j.date()
    one_day = timedelta(days=1)
    for item in data:
        item['Date'] = start_date
        item['Open'] = item.pop('o')
        item['Close'] = item.pop('c')
        item['High'] = item.pop('h')
        item['Low'] = item.pop('l')
        
        start_date += one_day

    return data

def place_order_stock(ib_client, order_list):
    order_status = False

    order_response = ib_client.place_orders(
        account_id=args.account_id,
        orders=order_list
    )

    if order_response:
        response_id_dict = order_response[0]
        reply_id = response_id_dict.get('id', None)

        if reply_id is not None:
            confirm = True
            reply_response = ib_client.place_order_reply(
                reply_id=reply_id,
                reply=confirm)
            order_status = True

    return order_status


def get_signal(dataframe, close_price):
    """ Function to get Sell or Buy signal."""
    if close_price > dataframe['Upper'][-1]: # SELL
        return "SELL"
    elif close_price < dataframe['Lower'][-1]: # BUY
        return "BUY"

    return "NAN"

def update_server_id(server_id):
    global SERVER_IDS
    SERVER_IDS.append(server_id)

def build_data_list(data):
    global DATA_LIST
    for item in data:
        DATA_LIST.append(item)

def empty_data_list():
    global DATA_LIST
    global DATA_FRAMES
    DATA_LIST = []
    DATA_FRAMES = []

def empty_server_id_list():
    global SERVER_IDS
    SERVER_IDS = []

def authenticate_ib_client(ib_client):
    global USERNAME
    global PASSWORD
    global AUTH_DONE

    if PASSWORD and not AUTH_DONE:
        try:
            ib_client.logout()
        except HTTPError as e:
            pass

        authenticated_accounts = auto_mode_on_accounts([USERNAME], [PASSWORD], sleep_sec=2)
        if authenticated_accounts:
            ib_client.is_authenticated()
            AUTH_DONE = True

    return ib_client

def convert_str_into_number(string, convert_into=float):
    try:
        return convert_into(string)
    except ValueError:
        string = string[1:]
        if convert_into == int:
            string = float(string)
        return convert_into(string)


def place_order_with_bollinger_band(current_close):
    global DATA_LIST, PERIOD
    global ACCOUNT, CONID
    global DATA_FRAMES
    global ib_client

    data_list = DATA_LIST
    period = PERIOD
    order_status = False

    current_close = convert_str_into_number(current_close)

    data_frames = bolliner_bands(data_list, period)

    if DATA_FRAMES:
        DATA_FRAMES.append(data_frames)

    side = get_signal(data_frames, current_close)

    if side == 'NAN':
        return order_status, side

    order_dict = {
        "secType": "secType = {}:STK".format(CONID),
        "orderType": "MKT",
        "listingExchange": "SMART",
        "isSingleGroup": True,
        "outsideRTH": False,
        "price": 0,
        "tif": "DAY",
        "referrer": "QuickTrade",
        "quantity": 1,
        "fxQty": 0,
        "useAdaptive": True,
        "isCcyConv": False,
        "allocationMethod": "AvailableEquity",
        "acctId": ACCOUNT,
        "conid": CONID,
        "side": side,
        "cOID": "OID-{}".format(random.randint(1,1000))
    }

    orders = {"orders" : [order_dict]}
    order_status = place_order_stock(ib_client, orders)

    return order_status, side

def extract_data_from_message(message):
    # two type of data for extraction
    # one message in market data and another message is current day stock

    # current day stock message
    if '31' in message:
        # do code go for bollinger
        current_close = message.get('31')
        order_placed, side = place_order_with_bollinger_band(convert_str_into_number(current_close))
        if order_placed:
            print("{} took place with CLOSING PRICE {}.".format(side, current_close))

    # market data message
    if 'timePeriod' in message:
        # do code
        server_id = message.get('serverId', None)
        if server_id is not None:
            update_server_id(server_id)

            data = message.get('data', [])
            start_date_str = message.get('startTime', '')
            if data:
                updated_data = update_data(data, start_date_str)
                build_data_list(updated_data)

def on_message(ws, message):
    message_dict = json.loads(message.decode('utf-8'))
    extract_data_from_message(message_dict)

def on_error(ws, error):
    global SERVER_IDS
    for server_id in SERVER_IDS:
        ws.send("umh+{}".format(server_id))

def on_close(ws, close_status_code, close_msg):
    print("{} exited with code {} and message {}.".format(ws, close_status_code, close_msg))

def on_open(ws):
    def run(*args):

        
        time_period_70days = 'smh+51529211+{"exchange":"NYSE","period":"70d","bar":"1d","outsideRth":false,"source":"t","format":"%h/%l/%c/%o"}'
        time_period_10days = 'smh+51529211+{"exchange":"NYSE","period":"15d","bar":"1d","outsideRth":false,"source":"t","format":"%h/%l/%c/%o"}'
        time_period_1days = 'smh+51529211+{"exchange":"NYSE","period":"2d","bar":"1d","outsideRth":false,"source":"t","format":"%h/%l/%c/%o"}'
        current_price_cmd = 'smd+51529211+{"fields":["31","70","71"]}'

        today_date_obj = datetime.now().date()
        fetched_market_data = False
        print_flag = True

        while True:
            global SERVER_IDS
            global DATA_FRAMES

            # Subscribe to Market Data
            while_today_date_obj = datetime.now().date()

            if today_date_obj == while_today_date_obj and not fetched_market_data:
                empty_data_list()
                print("Sending request to MARKET DATA for date {}...".format(today_date_obj))

                time.sleep(5)
                ws.send(time_period_70days)
                time.sleep(5)
                ws.send(time_period_10days)
                time.sleep(5)
                ws.send(time_period_1days)
                time.sleep(5)

                fetched_market_data = True

            elif today_date_obj != while_today_date_obj and not fetched_market_data:
                empty_data_list()
                print("Sending request to MARKET DATA for date {}...".format(today_date_obj))

                time.sleep(5)
                ws.send(time_period_70days)
                time.sleep(5)
                ws.send(time_period_10days)
                time.sleep(5)
                ws.send(time_period_1days)
                time.sleep(5)

                today_date_obj = while_today_date_obj
                fetched_market_data = True

            elif today_date_obj != while_today_date_obj and fetched_market_data:
                fetched_market_data = False
                print_flag = False
            else:
                print("MARKET DATA already fetched for date {}...".format(today_date_obj))
                if print_flag and DATA_FRAMES:
                    print_df(DATA_FRAMES[0])
                    print_flag = False

            # Unsubscribe
            for server_id in SERVER_IDS:
                print("Sending unsubscribe request for SERVER ID {}...".format(server_id))
                unsub_str = "umh+{}".format(server_id)
                ws.send(unsub_str)
                time.sleep(2)

            if SERVER_IDS:
                empty_server_id_list()

            # Current Close Price
            if fetched_market_data:
                ws.send(current_price_cmd)
                time.sleep(60)

        # ws.close()
    _thread.start_new_thread(run, ())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Buy or Sell stock with Interactive Brokers.')
    parser.add_argument('--username', required=True, help='YOUR_USERNAME')
    parser.add_argument('--account-id', required=True, help='YOUR_ACCOUNT_NUMBER')
    parser.add_argument('--conid', required=True, type=int, help='STOCK_CONTRACT_ID')
    parser.add_argument('--passkey', help='YOUR_PASSWORD')

    args = parser.parse_args()

    USERNAME = args.username
    PASSWORD = args.passkey
    ACCOUNT = args.account_id
    CONID = args.conid

    # Create a new session of the IB Web API.
    ib_client = IBClient(
        username=USERNAME,
        account=PASSWORD,
        is_server_running=True
    )
    ib_client = authenticate_ib_client(ib_client)

    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(URL,
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)

    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
