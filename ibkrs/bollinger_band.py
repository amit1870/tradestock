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
from stock_config import BOLLINGER_CONF
from utils.helper import print_df

def main(ib_client, args):

    stock_obj = Stock(ib_client)

    contract_ids = []
    symbols = []

    if not args.conid:

        # grab account portfolios
        try:    
            account_positions = ib_client.portfolio_account_positions(
                account_id=args.account_id,
                page_id=0
            )
        except HTTPError as e:
            account_positions = []

        for row in account_positions:
            for key, val in row.items():
                if key == 'conid':
                    contract_ids.append(val)
                elif key == 'contractDesc':
                    symbols.append(val)
    else:
        contract_ids.append(args.conid)

    time_period = BOLLINGER_CONF['time-period']
    period = BOLLINGER_CONF['period']
    bar = BOLLINGER_CONF['bar']
    upper = BOLLINGER_CONF['upper']
    lower = BOLLINGER_CONF['lower']

    if args.time_period:
        time_period = args.time_period

    if args.bar:
        bar = args.bar

    if args.upper:
        upper = args.upper

    if args.lower:
        lower = args.lower

    for idx, conid in enumerate(contract_ids):

        data_list = stock_obj.get_market_data_history_list(conid, time_period, bar)

        if data_list:

            bolinger_frame = hp.get_bollinger_band(data_list, period, upper, lower, plot=True)

            if args.conid:
                print_df(bolinger_frame)
            else:
                print("Bollinger Decision for contract id {}({})".format(conid, symbols[idx]))
                print()
                print(bolinger_frame.tail(5))
        else:
            print("Market data snapshot history empty for contract id {}({}).".format(conid, symbols[idx]))

    else:
        stock_obj.ib_client.unsubscribe_all_market_data_history()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Buy or Sell stock with Interactive Brokers.')
    parser.add_argument('--username', required=True, help='YOUR_USERNAME')
    parser.add_argument('--account-id', required=True, help='YOUR_ACCOUNT_NUMBER')
    parser.add_argument('--conid', type=int, help='STOCK_CONTRACT_ID')
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
        ib_client, auth_status = hp.authenticate_ib_client(ib_client, [args.username], [args.passkey], hard=True)

    main(ib_client, args)
