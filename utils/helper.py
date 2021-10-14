"""
This module will contain helping functions.
"""
import os
import contextlib
import sys
import os

from requests.exceptions import HTTPError
from .auto_mode import auto_mode_on_accounts


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
        
        start_date += one_day

    return data

def authenticate_ib_client(ib_client, usernames, passwords):
    try:
        ib_client.logout()
    except HTTPError as e:
        pass

    authenticated_accounts = auto_mode_on_accounts(usernames, passwords, sleep_sec=2)
    if authenticated_accounts:
        ib_client.is_authenticated()

    return ib_client