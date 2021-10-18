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

URL = "wss://localhost:5000/v1/api/ws"
SERVER_IDS = []
DATA_FRAMES = []
PERIOD = 12 # 12-Day Moving Average
STD_FACTOR_UPPER = 2 # 2 Standard Deviation
STD_FACTOR_LOWER = 2 # 2 Standard Deviation
AUTH_DONE = False
DATA_LIST = []
HOUR = 3600 # seconds
SHORT_SLEEP = HOUR // 30
NAP_SLEEP = SHORT_SLEEP // 2 
data_from_31_flag = True

config = os.environ.get('CONFIG', 'Testing')
if config == 'Testing':
    SHORT_SLEEP = SHORT_SLEEP / 2
    NAP_SLEEP = NAP_SLEEP / 2

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

def add_single_data_to_data_list(data):
    global DATA_LIST
    DATA_LIST.append(data)

def update_last_index_close_price(close_price):
    global DATA_LIST
    if DATA_LIST:
        last_item = DATA_LIST[-1]
        last_item['Close'] = close_price


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

def calculate_next_period():
    global DATA_LIST

    period = 1
    if DATA_LIST:
        last_data = DATA_LIST[-1]
        last_date = last_data.get('Date')
        last_date_obj = last_date
        today_date_obj = datetime.now().date()

        days_delta = today_date_obj - last_date_obj
        period = days_delta.days - 1

    return period


def place_order_with_bollinger_band(current_close):
    global DATA_LIST, PERIOD
    global ACCOUNT, CONID
    global DATA_FRAMES
    global stock_obj
    global STD_FACTOR_LOWER, STD_FACTOR_UPPER

    data_list = DATA_LIST
    period = PERIOD
    order_status = {}
    quantity = 0

    data_frames = bolliner_bands(data_list, period, STD_FACTOR_LOWER, STD_FACTOR_UPPER)

    if DATA_FRAMES == []:
        DATA_FRAMES.append(data_frames)

    side = get_signal(data_frames, current_close)
    if side == 'NAN':
        return order_status, side

    elif side == 'SELL': # SELL
        stock_postion = stock_obj.search_stock_by_conid(ACCOUNT, CONID)

        if stock_postion:
            quantity = stock_postion.get('position', 0)

    else: # BUY
        # get balance and calculate number of position to buy
        balance_type = 'AVB'
        account_balance_dict = stock_obj.get_account_balance(ACCOUNT, balance_type)
        account_balance = account_balance_dict.get('amount', 0)
        quantity = account_balance // current_close

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

    global data_from_31_flag

    # current day stock message
    if '31' in message:
        # do code go for bollinger
        current_close = message.get('31')
        current_close = hp.convert_str_into_number(current_close)

        if data_from_31_flag:
            current_open = current_close
            current_high = message.get('70', current_close)
            current_high = hp.convert_str_into_number(current_high)

            current_low = message.get('71', current_close)
            current_low = hp.convert_str_into_number(current_low)

            # added a condition when market is not open
            if current_high == 0:
                current_high = current_close
                current_low = current_close

            current_day_data_dict = {
                'Date': datetime.now().date(),
                'High': current_high,
                'Low': current_low,
                'Open': current_open,
                'Close': current_close
            }
            add_single_data_to_data_list(current_day_data_dict)
            data_from_31_flag = False
        else:
            update_last_index_close_price(current_close)

        print("RUNNING BOLLINGER BANDS with CLOSING PRICE at [{}]".format(current_close))

        order_placed, side = place_order_with_bollinger_band(current_close)
        if order_placed and side == 'SELL':
            print("{} took place at CLOSING PRICE {} with message {}.".format(side, current_close, order_placed))
            print("PROFIT !! PROFIT !! PROFIT !! PROFIT !! PROFIT !! PROFIT !! PROFIT !! PROFIT !! .".format(side, current_close, order_placed))
        elif order_placed and side == 'BUY':
            print("{} took place at CLOSING PRICE {} with message {}.".format(side, current_close, order_placed))
            print("BUYED !! BUYED !! BUYED !! BUYED !! BUYED !! BUYED !! BUYED !! BUYED !! .".format(side, current_close, order_placed))
        else:
            print("CLOSING PRICE at [{}] does not XXXXX BOLLINGER BANDS.".format(current_close))

    # market data messages
    elif 'timePeriod' in message:
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
        time.sleep(NAP_SLEEP)

def on_close(ws, close_status_code, close_msg):
    print("{} exited with code {} and message {}.".format(ws, close_status_code, close_msg))

def on_open(ws):
    def run(*args):
        global CONID
        global TIME_PERIOD
        global BAR

        cmd_str_template = 'smh+{}+{{"exchange":"NYSE","period":"{}","bar":"{}","outsideRth":false,"source":"t","format":"%h/%l/%c/%o"}}'
        cmd_str = cmd_str_template.format(CONID, TIME_PERIOD, BAR)

        current_price_cmd = 'smd+{}+{{"fields":["31","70","71"]}}'.format(CONID)

        today_date_obj = datetime.now().date()
        fetched_market_data = False
        print_flag = True

        while True:
            global SERVER_IDS
            global DATA_FRAMES
            global DATA_LIST
            global data_from_31_flag

            # Subscribe to Market Data
            while_today_date_obj = datetime.now().date()

            if today_date_obj == while_today_date_obj and not fetched_market_data:
                empty_data_list()
                time.sleep(NAP_SLEEP)
                print("SEND SUBSCRIBE REQUEST to MARKET DATA for date {}...".format(today_date_obj))
                ws.send(cmd_str)
                time.sleep(NAP_SLEEP)
                bar_type = BAR[-1]
                if bar_type == 'd':
                    calculated_period = calculate_next_period()
                    calculated_period = "{}{}".format(calculated_period, bar_type)
                    cmd_str = cmd_str_template.format(CONID, calculated_period, BAR)
                    ws.send(cmd_str)

                fetched_market_data = True

            elif today_date_obj != while_today_date_obj and not fetched_market_data:
                empty_data_list()
                time.sleep(NAP_SLEEP)
                print("SEND SUBSCRIBE REQUEST to MARKET DATA for date {}...".format(today_date_obj))
                ws.send(cmd_str)
                time.sleep(NAP_SLEEP)
                bar_type = BAR[-1]
                if bar_type == 'd':
                    calculated_period = calculate_next_period()
                    calculated_period = "{}{}".format(calculated_period, bar_type)
                    cmd_str = cmd_str_template.format(CONID, calculated_period, BAR)
                    ws.send(cmd_str)
                today_date_obj = while_today_date_obj
                fetched_market_data = True

            elif today_date_obj != while_today_date_obj and fetched_market_data:
                fetched_market_data = False
                print_flag = True
                data_from_31_flag = True
            else:
                print("MARKET DATA already fetched for date {}...".format(today_date_obj))
                if print_flag and DATA_FRAMES:
                    hp.print_df(DATA_FRAMES[0])
                    print_flag = False

            # Unsubscribe
            for server_id in SERVER_IDS:
                print("SEND UNSUBUSCRIBE REQUEST for SERVER ID {}...".format(server_id))
                unsub_cmd = "umh+{}".format(server_id)
                ws.send(unsub_cmd)
                time.sleep(NAP_SLEEP)

            if SERVER_IDS:
                empty_server_id_list()

            # Current Close Price
            if fetched_market_data:
                ws.send(current_price_cmd)
                time.sleep(SHORT_SLEEP)

        # ws.close()
    _thread.start_new_thread(run, ())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Buy or Sell stock with Interactive Brokers.')
    parser.add_argument('--username', required=True, help='YOUR_USERNAME')
    parser.add_argument('--account-id', required=True, help='YOUR_ACCOUNT_NUMBER')
    parser.add_argument('--conid', required=True, type=int, help='STOCK_CONTRACT_ID')
    parser.add_argument('--passkey', help='YOUR_PASSWORD')
    parser.add_argument('--time-period', default='93d', help='Time period for Market Data')
    parser.add_argument('--period', default=12, type=int, help='Moving Average number')
    parser.add_argument('--bar', default='1d', help='Bar')
    parser.add_argument('--upper', default=0.7, type=float, help='STD Upper Factor')
    parser.add_argument('--lower', default=0.7, type=float, help='STD Lower Factor')

    args = parser.parse_args()

    USERNAME = args.username
    PASSWORD = args.passkey
    ACCOUNT = args.account_id
    CONID = args.conid
    TIME_PERIOD = args.time_period
    PERIOD = args.period
    BAR = args.bar
    STD_FACTOR_UPPER = args.upper
    STD_FACTOR_LOWER = args.lower

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
