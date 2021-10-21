"""
This module will contain helping functions.
"""
import os
import contextlib
import sys
import os

from datetime import datetime, timedelta
from requests.exceptions import HTTPError
from .auto_mode import auto_mode_on_accounts


remove_n = lambda ch : ch != '\n'

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
    for idx, line in enumerate(lines):
        line = convert_space_to_html_code(line)
        line = line[:-1]
        if len(line):
            if idx > 2:
                if not line.startswith(dash) and \
                    (headers_start not in line) and \
                    (auth_fail_msg not in line) and\
                    (not line.startswith(space_only)):
                    new_parsed_content.append(line)
            else:
                headers.append(line)

    headers = "<br/>".join(headers)
    new_parsed_content = list(filter(remove_n, new_parsed_content))
    new_parsed_content = "<br/><br/>".join(new_parsed_content)

    return headers + "<br/>"+ new_parsed_content
