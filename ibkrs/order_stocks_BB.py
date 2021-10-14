"""
This script will place order using real time price of stock.
Decision to place order will be done by Bollinger Band strategy.
"""
import os
import websocket
import ssl
import random
import _thread
import time
import json
import argparse
import logging

from requests.exceptions import HTTPError
from datetime import datetime
from ibw.client import IBClient
from order_algo import bolliner_bands
from utils import helper as hp
from stock import Stock

plt.style.use('fivethirtyeight')


URL = "wss://localhost:5000/v1/api/ws"

SERVER_IDS = []
DATA_FRAMES = []
PERIOD = 3
AUTH_DONE = False
DATA_LIST = []
STD_FACTOR_UPPER = 0.5
STD_FACTOR_LOWER = 0.5
HOUR = 3600 # seconds
LONG_SLEEP = 1 * HOUR
SHORT_SLEEP = HOUR / 360


config = os.environ.get('CONFIG', 'Testing')
if config == 'Testing':
    LONG_SLEEP = LONG_SLEEP / 60

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
        ib_client, auth_status = hp.authenticate_ib_client(ib_client, [USERNAME], [PASSWORD])
        AUTH_DONE = True

    return ib_client, auth_status

def place_order_with_bollinger_band(current_close):
    global DATA_LIST, PERIOD
    global ACCOUNT, CONID
    global DATA_FRAMES
    global stock_obj

    data_list = DATA_LIST
    period = PERIOD
    order_status = False
    quantity = 0

    data_frames = bolliner_bands(data_list, period)

    if DATA_FRAMES == []:
        DATA_FRAMES.append(data_frames)

    side = get_signal(data_frames, current_close)

    if side == 'NAN':
        return order_status, side

    if side == 'SELL':
        stock_postion = stock_obj.search_stock_by_conid(ACCOUNT, CONID)

        if stock_postion:
            quantity = stock_postion.get('position', 0)

    if side == 'BUY':
        # get balance and calculate number of position to buy
        balance_type = 'AVB'
        account_balance_dict = stock_obj.get_account_balance(ACCOUNT, balance_type)
        account_balance = account_balance_dict.get('amount', 0)
        quantity = account_balance / current_close

    order_dict = {
        "secType": "secType = {}:STK".format(CONID),
        "orderType": "MKT",
        "listingExchange": "SMART",
        "isSingleGroup": True,
        "outsideRTH": False,
        "price": 0,
        "tif": "DAY",
        "referrer": "QuickTrade",
        "quantity": quantity,
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
    order_status = stock_obj.place_order_stock(ACCOUNT, orders)
    
    return order_status, side

def extract_data_from_message(message):
    # two type of data for extraction
    # one message in market data and another message is current day stock

    # current day stock message
    if '31' in message:
        # do code go for bollinger
        current_close = message.get('31')
        order_placed, side = place_order_with_bollinger_band(hp.convert_str_into_number(current_close))
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
                updated_data = hp.update_data(data, start_date_str)
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
        time_period_1days = 'smh+51529211+{"exchange":"NYSE","period":"5d","bar":"1d","outsideRth":false,"source":"t","format":"%h/%l/%c/%o"}'
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

                time.sleep(SHORT_SLEEP)
                ws.send(time_period_70days)
                time.sleep(SHORT_SLEEP)
                ws.send(time_period_10days)
                time.sleep(SHORT_SLEEP)
                ws.send(time_period_1days)
                time.sleep(SHORT_SLEEP)

                fetched_market_data = True

            elif today_date_obj != while_today_date_obj and not fetched_market_data:
                empty_data_list()
                print("Sending request to MARKET DATA for date {}...".format(today_date_obj))

                time.sleep(SHORT_SLEEP)
                ws.send(time_period_70days)
                time.sleep(SHORT_SLEEP)
                ws.send(time_period_10days)
                time.sleep(SHORT_SLEEP)
                ws.send(time_period_1days)
                time.sleep(SHORT_SLEEP)

                today_date_obj = while_today_date_obj
                fetched_market_data = True

            elif today_date_obj != while_today_date_obj and fetched_market_data:
                fetched_market_data = False
                print_flag = True
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
                time.sleep(SHORT_SLEEP)

            if SERVER_IDS:
                empty_server_id_list()

            # Current Close Price
            if fetched_market_data:
                ws.send(current_price_cmd)
                time.sleep(LONG_SLEEP)

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
        username=args.username,
        account=args.account_id,
        is_server_running=True
    )
    auth_status = False
    if args.passkey:
        ib_client, auth_status = hp.authenticate_ib_client(ib_client, [args.username], [args.passkey])

    if not args.passkey:
        stock_obj = Stock(ib_client)
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp(URL,
                                  on_open=on_open,
                                  on_message=on_message,
                                  on_error=on_error,
                                  on_close=on_close)

        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    elif auth_status:
        stock_obj = Stock(ib_client)
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp(URL,
                                  on_open=on_open,
                                  on_message=on_message,
                                  on_error=on_error,
                                  on_close=on_close)

        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
