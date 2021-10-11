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

Fig1 = "/home/ec2-user/virenv/fig1.jpg"
Fig2 = "/home/ec2-user/virenv/fig2.jpg"
Fig3 = "/home/ec2-user/virenv/fig3.jpg"

SERVER_IDS = []
PERIOD = 20
AUTH_DONE = False

def add_date_to_data(data, start_date_str):
    """ Add Date to each item of list."""
    start_date_j = datetime.strptime(start_date_str, '%Y%m%d-%H:%M:%S')
    start_date = start_date_j.date()
    one_day = timedelta(days=1)
    for item in data:
        item['Date'] = start_date
        start_date += one_day

    return data

def place_order_stock(ib_client, order_dict):
    order_status = False
    return order_status
    order_response = ib_client.place_orders(
        account_id=args.account_id,
        orders=order_dict
    )
    if order_response:
        response_id_dict = order_response[0]
        reply_id = response_id_dict.get('id', None)

        if reply_id is not None:
            reply = {'confirmed' : confirmation}
            reply_response = ib_client.place_order_reply(
                reply_id=reply_id,
                reply=confirmation)
            order_status = True

    return order_status


def get_signal(ib_client, data):
    """ Function to get Sell or Buy signal."""
    global ACCOUNT
    buy_signal = [] # buy list
    sell_signal = [] # sell list

    order_dict = {
        "secType": "secType = 51529211:STK",
        "orderType": "MKT",
        "listingExchange": "SMART",
        "isSingleGroup": True,
        "outsideRTH": False,
        "price": 0,
        "ticker": "GLD",
        "tif": "DAY",
        "referrer": "QuickTrade",
        "quantity": 1,
        "fxQty": 0,
        "useAdaptive": True,
        "isCcyConv": False,
        "allocationMethod": "AvailableEquity",
        "acctId": ACCOUNT,
        "conid": "51529211",
        "side": "BUY",
        "cOID": "OID-{}".format(random.randint(1,1000))
    }

    for i in range(len(data['c'])):
        # Sell
        if data['c'][i] > data['h'][i]:
            buy_signal.append(np.nan)
            sell_signal.append(data['c'][i])
            order_dict['side'] = 'SELL'
            orders = {"orders" : [order_dict]}
            place_order_stock(ib_client, orders)
 
        # Buy
        elif data['c'][i] < data['l'][i]:
            sell_signal.append(np.nan)
            buy_signal.append(data['c'][i])
            order_dict['side'] = 'BUY'
            orders = {"orders" : [order_dict]}
            place_order_stock(ib_client, order_dict)
        else:
            buy_signal.append(np.nan)
            sell_signal.append(np.nan)

    return buy_signal, sell_signal

def bolliner_bands(data_frame, ib_client, period=20):
    df = data_frame

    # set the date as the index
    df = df.set_index(pd.DatetimeIndex(df['Date'].values))

    # Calculate Simple Moving Average, Std Deviation, h Band and l Band
    df['SMA'] = df['c'].rolling(window=period).mean()

    df['STD'] = df['c'].rolling(window=period).std()

    df['h'] = df['SMA'] + (df['STD'] * 2)

    df['l'] = df['SMA'] - (df['STD'] * 2)

    column_list = ['c', 'SMA', 'h', 'l']

    df[column_list].plot(figsize=(12.2,6.4))

    plt.title('Bollinger Bands')

    plt.ylabel('USD Price ($)')

    plt.savefig(Fig1)

    # plot and shade the area between the two Bollinger bands
    fig = plt.figure(figsize=(12.2,6.4)) # width = 12.2" and height = 6.4"

    # Add the subplot
    ax = fig.add_subplot(1,1,1) # number of rows, cols and index

    # Get the index values of the DataFrame
    x_axis = df.index

    # plot and shade the area between the upper band and the lower band Grey
    ax.fill_between(x_axis, df['h'], df['l'], color='grey')

    # plot the Closing Price and Moving Average
    ax.plot(x_axis, df['c'], color='gold', lw=3, label = 'c Price') #lw = line width

    ax.plot(x_axis, df['SMA'], color='blue', lw=3, label = 'Simple Moving Average')

    # Set the Title & Show the Image
    ax.set_title('Bollinger Bands')
    ax.set_xlabel('Date')
    ax.set_ylabel('USD Price ($)')
    plt.xticks(rotation = 45)
    ax.legend()
    plt.savefig(Fig2)

    # create a new data frame
    new_df = df[period-1:]


    # create new columns for the buy and sell signals
    buy_signal, sell_signal = get_signal(ib_client, new_df)
    new_df['Buy'] = buy_signal
    new_df['Sell'] = sell_signal

    fig = plt.figure(figsize=(12.2,6.4))
    ax = fig.add_subplot(1,1,1)
    x_axis = new_df.index

    # plot and shade the area between the upper band and the lower band Grey
    ax.fill_between(x_axis, new_df['h'], new_df['l'], color='grey')

    # plot the Closing Price and Moving Average
    ax.plot(x_axis, new_df['c'], color='gold', lw=3, label = 'Close Price',alpha = 0.5)
    ax.plot(x_axis, new_df['SMA'], color='blue', lw=3, label = 'Moving Average',alpha = 0.5)
    ax.scatter(x_axis, new_df['Buy'] , color='green', lw=3, label = 'Buy',marker = '^', alpha = 1)
    ax.scatter(x_axis, new_df['Sell'] , color='red', lw=3, label = 'Sell',marker = 'v', alpha = 1)

    # set the Title and Show the Image
    ax.set_title('Bollinger Bands')
    ax.set_xlabel('Date')
    ax.set_ylabel('USD Price ($)')
    plt.xticks(rotation = 45)
    ax.legend()
    plt.savefig(Fig3)

def on_message(ws, message):

    global SERVER_IDS, PERIOD, USERNAME, PASSWORD, AUTH_DONE, ib_client

    message_dict = json.loads(message.decode('utf-8'))
    SERVER_ID = message_dict.get('serverId', None)

    if SERVER_ID is not None:
        SERVER_IDS.append(SERVER_ID)
    print("SERVER_ID : {}".format(SERVER_IDS))

    if PASSWORD and not AUTH_DONE:
        try:
            ib_client.logout()
        except HTTPError as e:
            pass

        authenticated_accounts = auto_mode_on_accounts([USERNAME], [PASSWORD], sleep_sec=2)
        if authenticated_accounts:
            ib_client.is_authenticated()
            AUTH_DONE = True

    data_list = message_dict.get('data', [])

    if data_list:
        start_date_str = message_dict.get('startTime')
        data_list = add_date_to_data(data_list, start_date_str)
        df = pd.DataFrame(data_list)
        # df = pd.read_csv(data_file_path)
        print("Getting Bollinger Bands for this cycle...")
        bolliner_bands(df, ib_client, period=PERIOD)
        print("Finished!!")


def on_error(ws, error):
    print("FROM ERROR :", error)

def on_close(ws, close_status_code, close_msg):
    print("{} exited with code {} and message {}.".format(ws, close_status_code, close_msg))

def on_open(ws):
    def run(*args):

        while True:
            global SERVER_IDS
            # ws.send('smd+51529211+{"fields":["55","7295",70","71","7296","7296","7762"]}')
            print("Sending request to Market Data...")
            ws.send('smh+51529211+{"exchange":"NYSE","period":"365d","bar":"1d","outsideRth":false,"source":"t","format":"%h/%l/%c/%o"}')
            time.sleep(20)
            for server_id in SERVER_IDS:
                print("Sending request to Unsubscribe Market Data...")
                ws.send('umh+{}'.format(server_id))
                time.sleep(60)

            SERVER_IDS = []
            
        # ws.close()
    _thread.start_new_thread(run, ())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Buy or Sell stock with Interactive Brokers.')
    parser.add_argument('--username', required=True, help='YOUR_USERNAME')
    parser.add_argument('--account-id', required=True, help='YOUR_ACCOUNT_NUMBER')
    parser.add_argument('--passkey', help='YOUR_PASSWORD')

    args = parser.parse_args()

    USERNAME = args.username
    PASSWORD = args.passkey
    ACCOUNT = args.account_id

    # Create a new session of the IB Web API.
    ib_client = IBClient(
        username=USERNAME,
        account=PASSWORD,
        is_server_running=True
    )

    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(URL,
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)

    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
