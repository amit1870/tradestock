"""
This script will provide Bollinger Band values for given contract id.
"""
import sys
import os
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from requests.exceptions import HTTPError
from datetime import datetime, timezone

from ibw.client import IBClient
from utils import helper as hp
from stock import Stock
from utils.helper import print_df


def main(ib_client, args):

    stock_obj = Stock(ib_client)

    data_frames = stock_obj.get_market_data_history_frame(args.conid, args.time_period, args.bar)

    if not data_frames.empty:
        stock_obj.ib_client.unsubscribe_all_market_data_history()
        bolinger_frame = hp.get_bollinger_band(data_frames, args.period, args.upper, args.lower, plot=True)
        print_df(bolinger_frame)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Buy or Sell stock with Interactive Brokers.')
    parser.add_argument('--username', required=True, help='YOUR_USERNAME')
    parser.add_argument('--account-id', required=True, help='YOUR_ACCOUNT_NUMBER')
    parser.add_argument('--conid', required=True, type=int, help='STOCK_CONTRACT_ID')
    parser.add_argument('--passkey', help='YOUR_PASSWORD')
    parser.add_argument('--time-period', default='100d', help='Time period for Market Data')
    parser.add_argument('--period', default=12, type=int, help='Moving Average number')
    parser.add_argument('--bar', default='1d', help='Bar')
    parser.add_argument('--upper', default=2, type=float, help='STD Upper Factor')
    parser.add_argument('--lower', default=2, type=float, help='STD Lower Factor')

    args = parser.parse_args()

    # Create a new session of the IB Web API.
    ib_client = IBClient(
        username=args.username,
        account=args.account_id,
        is_server_running=True
    )
    auth_status = False
    if args.passkey:
        ib_client, auth_status = hp.authenticate_ib_client(ib_client, [args.username], [args.passkey])

    main(ib_client, args)
