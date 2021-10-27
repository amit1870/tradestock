"""
This module will contain helping functions.
"""
import os
import contextlib
import sys
import os
import time
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime, timedelta, timezone
from requests.exceptions import HTTPError

from .auto_mode import auto_mode_on_accounts
from utils.settings import ACCOUNTS, BASE_DIR
from stock_config import ORDERS
from utils.lsr_opr import get_context, decrypt_lsr

NEW_LINE_CHAR = '\n'
SPACE = ' '

remove_n = lambda ch : ch != NEW_LINE_CHAR
remove_space = lambda ch: ch != SPACE

pd.options.mode.chained_assignment = None  # default='warn'
plt.style.use('fivethirtyeight')
plt.rcParams.update({'figure.max_open_warning': 0})


def get_authenticated_accounts(usernames, passwords):
    context = get_context()
    authenticated_accounts = []

    for idx,username in enumerate(usernames):    
        accounts = [account for key, account in ACCOUNTS.items()]

        for account in accounts:
            account_lsr = account.get('lsr')
            passkey = passwords[idx]
            if account.get('username') == username and decrypt_lsr(context, passkey, account_lsr):
                    account['lsr'] = passkey
                    authenticated_accounts.append(account)
                    break
            elif account.get('username') == username and not decrypt_lsr(context, passkey, account_lsr):
                break

    return authenticated_accounts

def supress_stdout(func):
    def wrapper(*a, **ka):
        with open(os.devnull, 'w') as devnull:
            with contextlib.redirect_stdout(devnull):
                func(*a, **ka)
    return wrapper

def print_df(data_frames, use_str=True):

    if use_str:
        print(data_frames.to_string())
    else:
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(data_frames)

def get_signal(df):
    """ Function to get Sell or Buy signal."""
    buy_signal = [] # buy list
    sell_signal = [] # sell list

    for i in range(len(df['Close'])):
        # Sell
        if df['Close'][i] > df['Upper'][i]:
            buy_signal.append(np.nan)
            sell_signal.append(df['Close'][i])
        # Buy
        elif df['Close'][i] < df['Lower'][i]:
            sell_signal.append(np.nan)
            buy_signal.append(df['Close'][i])
        else:
            buy_signal.append(np.nan)
            sell_signal.append(np.nan)

    return buy_signal, sell_signal

def get_signal_for_last_frame(df, close_price):
    """ Function to get Sell or Buy signal."""
    if close_price > df['Upper'][-1]: # SELL
        return "SELL"
    elif close_price < df['Lower'][-1]: # BUY
        return "BUY"

    return "NAN"

def get_bollinger_band(data_list, period, upper, lower, plot=False):

    df = pd.DataFrame(data_list)

    # set the date as the index
    df = df.set_index(pd.DatetimeIndex(df['Date'].values))

    # Calculate Simple Moving Average, Std Deviation, Upper Band and Lower Band
    df['SMA'] = df['Close'].rolling(window=period).mean()

    df['STD'] = df['Close'].rolling(window=period).std()

    df['Upper'] = df['SMA'] + (df['STD'] * upper)

    df['Lower'] = df['SMA'] - (df['STD'] * lower)

    # create a new data frame
    new_df = df[period-1:]

    if plot:
        column_list = ['Close', 'SMA', 'Upper', 'Lower']

        df[column_list].plot(figsize=(12.2,6.4))

        plt.title('Bollinger Bands')

        plt.ylabel('USD Price ($)')

        figure = "{}/fig1.jpg".format(BASE_DIR.as_posix())
        plt.savefig("{}".format(figure))
        plt.close(figure)

        # plot and shade the area between the two Bollinger bands
        fig = plt.figure(figsize=(12.2,6.4)) # width = 12.2" and height = 6.4"

        # Add the subplot
        ax = fig.add_subplot(1,1,1) # number of rows, cols and index

        # Get the index values of the DataFrame
        x_axis = df.index

        # plot and shade the area between the upper band and the lower band Grey
        ax.fill_between(x_axis, df['Upper'], df['Lower'], color='grey')

        # plot the Closing Price and Moving Average
        ax.plot(x_axis, df['Close'], color='gold', lw=3, label = 'Close Price') #lw = line width

        ax.plot(x_axis, df['SMA'], color='blue', lw=3, label = 'Simple Moving Average')

        # Set the Title & Show the Image
        ax.set_title('Bollinger Bands')
        ax.set_xlabel('Date')
        ax.set_ylabel('USD Price ($)')
        plt.xticks(rotation = 45)
        ax.legend()

        figure = "{}/fig2.jpg".format(BASE_DIR.as_posix())
        plt.savefig("{}".format(figure))
        plt.close(figure)

        # create new columns for the buy and sell signals
        buy_signal, sell_signal = get_signal(new_df)
        new_df['Buy'] = buy_signal
        new_df['Sell'] = sell_signal

        fig = plt.figure(figsize=(12.2,6.4))
        ax = fig.add_subplot(1,1,1)
        x_axis = new_df.index

        # plot and shade the area between the upper band and the lower band Grey
        ax.fill_between(x_axis, new_df['Upper'], new_df['Lower'], color='grey')

        # plot the Closing Price and Moving Average
        ax.plot(x_axis, new_df['Close'], color='gold', lw=3, label = 'Close Price',alpha = 0.5)
        ax.plot(x_axis, new_df['SMA'], color='blue', lw=3, label = 'Moving Average',alpha = 0.5)
        ax.scatter(x_axis, new_df['Buy'] , color='green', lw=3, label = 'Buy',marker = '^', alpha = 1)
        ax.scatter(x_axis, new_df['Sell'] , color='red', lw=3, label = 'Sell',marker = 'v', alpha = 1)

        # set the Title and Show the Image
        ax.set_title('Bollinger Bands')
        ax.set_xlabel('Date')
        ax.set_ylabel('USD Price ($)')
        plt.xticks(rotation = 45)
        ax.legend()

        figure = "{}/fig3.jpg".format(BASE_DIR.as_posix())
        plt.savefig("{}".format(figure))
        plt.close(figure)

    return new_df

def convert_str_into_number(string, convert_into=float):
    try:
        return convert_into(string)
    except ValueError:
        string = string[1:]
        if convert_into == int:
            string = float(string)
        return convert_into(string)

def update_data(data, start_date_str):
    """ add date start with argument to each item of list."""
    start_date_j = datetime.strptime(start_date_str, '%Y%m%d-%H:%M:%S')
    start_date = start_date_j.date()
    one_day = timedelta(days=1)
    for item in data:
        item['Date'] = start_date
        item['Open'] = item.pop('o')
        item['Close'] = item.pop('c')
        item['High'] = item.pop('h')
        item['Low'] = item.pop('l')
        
        weekday = start_date.weekday()
        if weekday == 4:
            start_date += one_day
            start_date += one_day

        start_date += one_day

    return data

def authenticate_ib_client(ib_client, usernames, passwords):
    auth_status = False
    attempt = 3
    try:
        ib_client.logout()
    except HTTPError as e:
        pass

    authenticated_accounts = auto_mode_on_accounts(usernames, passwords, sleep_sec=2)
    if authenticated_accounts:
        while attempt and not auth_status:
            auth_response = ib_client.is_authenticated()
            if 'authenticated' in auth_response.keys() and auth_response['authenticated']:
                auth_status = True

            if not auth_status:
                ib_client.reauthenticate()

            attempt -= 1
    
    return ib_client, auth_status

def reauthenticate_ib_client(ib_client):
    auth_status = False
    attempt = 3

    while attempt and not auth_status:
        auth_response = ib_client.is_authenticated()
        if 'authenticated' in auth_response.keys() and auth_response['authenticated']:
            auth_status = True

        if not auth_status:
            ib_client.reauthenticate()

        attempt -= 1
    
    return ib_client, auth_status

def get_datetime_obj_in_str(date_obj=None, seprator='-'):
    str_format = '%Y{}%m{}%d %H:%M:%S'.format(seprator, seprator)
    if date_obj is None:
        date_obj = datetime.today()

    return date_obj.strftime(str_format)

def convert_space_to_html_code(string):
    string_chr = []
    for ch in string:
        if ch == ' ':
            string_chr.append('&nbsp;')
        else:
            string_chr.append(ch)

    return "".join(string_chr)


def parse_file_output(output_file):
    try:
        with open(output_file) as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []

    headers = []
    new_parsed_content = []

    dash = "---"
    headers_start = "AccountID"
    auth_fail_msg = "Authentication"
    space_only = "&nbsp;"
    profit_tag = 'PF'
    for idx, line in enumerate(lines):
        line = convert_space_to_html_code(line)
        line = line[:-1]
        if len(line):
            if idx > 3:
                if not line.startswith(dash) and \
                    (headers_start not in line) and \
                    (auth_fail_msg not in line) and\
                    (not line.startswith(space_only)):
                    if profit_tag in line:
                        line = "<b><p style='color:#28a745;'>" + line + "</p></b>"
                    else:
                        line = "<p style='color:#e83e8c;'>" + line + "</p>"

                    new_parsed_content.append(line)
            else:
                line = "<b><p style='color:#6c757d;'>" + line + "</p></b>"
                headers.append(line)

    headers = "".join(headers)
    new_parsed_content = list(filter(remove_n, new_parsed_content))
    new_parsed_content = "".join(new_parsed_content)

    return headers + new_parsed_content

def get_current_time_in_ms():
    return int(time.time() * 1000)


def update_current_market_data(data):
    if '31' in data:
        current_open = convert_str_into_number(data.pop('31'))
    elif '71' in data:
        current_open = convert_str_into_number(data.pop('71'))

    current_high = convert_str_into_number(data.pop('70',current_open))
    current_low = convert_str_into_number(data.pop('71',current_open))

    if current_high == 0 or current_low == 0:
        current_low = current_open
        current_high = current_open


    timestamp_ms = data.pop('_updated') / 1000
    t_date = datetime.fromtimestamp(int(timestamp_ms), timezone.utc)

    data = {}
    data['Date'] = t_date.date()
    data['Open'] = current_open
    data['Close'] = current_open
    data['High'] = current_high
    data['Low'] = current_low

    return data


def prepare_order_dict_from_args(args_dict):
    # Update ORDERS dictionary
    ORDERS['acctId'] = args_dict.get('account_id')
    ORDERS['conid'] = args_dict.get('conid')
    ORDERS['side'] = args_dict.get('side')


    ORDERS['cOID'] = "ORDER-ID-{}".format(random.randint(313,919))
    ORDERS['ticker'] = "{}".format(args_dict.get('conid'))
    ORDERS['secType'] = "secType = {}:STK".format(args_dict.get('conid'))

    if 'ticker' in args_dict:
        ORDERS['ticker'] = args_dict.get('ticker')

    if 'sec_type' in args_dict:
        ORDERS['secType'] = args_dict.get('sec_type')

    if 'order_type' in args_dict:
        ORDERS['orderType'] = args_dict.get('order_type')

    if 'quantity' in args_dict:
        ORDERS['quantity'] = args_dict.get('quantity')

    if 'listingExchange' in args_dict:
        ORDERS['listingExchange'] = args_dict.get('listingExchange')

    if 'isSingleGroup' in args_dict:
        ORDERS['isSingleGroup'] = args_dict.get('isSingleGroup')

    if 'outsideRTH' in args_dict:
        ORDERS['outsideRTH'] = args_dict.get('outsideRTH')

    if 'price' in args_dict:
        ORDERS['price'] = args_dict.get('price')

    if 'referrer' in args_dict:
        ORDERS['referrer'] = args_dict.get('referrer')

    if 'useAdaptive' in args_dict:
        ORDERS['useAdaptive'] = args_dict.get('useAdaptive')

    if 'allocationMethod' in args_dict:
        ORDERS['allocationMethod'] = args_dict.get('allocationMethod')

    if 'tif' in args_dict:
        ORDERS['tif'] = args_dict.get('tif')

    orders = {"orders" : [ORDERS]}

    return orders