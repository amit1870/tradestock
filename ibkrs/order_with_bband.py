"""
This script will provide Bollinger Band values for given contract id.
"""
import sys
import os
import argparse
import time
import textwrap
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from requests.exceptions import HTTPError
from datetime import datetime, timezone

from ibw.client import IBClient
from utils import helper as hp
from stock import Stock
from utils.helper import print_df
from utils.settings import BOLLINGER_LOG_FILE

MINUTE = 60 # Seconds
NAP_SLEEP = MINUTE * 1

logging.basicConfig(
    filename=BOLLINGER_LOG_FILE.as_posix(),
    format='%(levelname)s - %(name)s - %(message)s',
    level=logging.DEBUG
)

def place_order_with_bollinger_band(stock_obj, account_id, conid, side, current_close):
    if side == 'SELL':
        stock_postion_dict = stock_obj.search_stock_by_conid(account_id, conid)
        quantity = stock_postion_dict.get('position', 0)

    else:
        # get balance and calculate number of position to buy
        balance_type = 'AVB'
        account_balance_dict = stock_obj.get_account_balance(account_id, balance_type)
        account_balance = account_balance_dict.get('amount', 0)
        quantity = account_balance // current_close

    order_dict = {
        'account_id': account_id,
        'conid': conid,
        'side': side,
        'quantity': quantity
    }

    orders = hp.prepare_order_dict_from_args(order_dict)
    order_status = stock_obj.place_order_stock(account_id, orders)

    return order_status

def main(ib_client, args):

    stock_obj = Stock(ib_client)

    conid = args.conid
    account_id = args.account_id

    market_data_list = stock_obj.get_market_data_history_list(conid, args.time_period, args.bar)


    if market_data_list:
        stock_obj.ib_client.unsubscribe_all_market_data_history()

        first_add_flag = True

        current_market_data = stock_obj.get_current_market_data_snapshot(conid)

        while current_market_data:

            snapshot_data = current_market_data[0]

            if '71' in  snapshot_data:

                current_close = hp.convert_str_into_number(snapshot_data.get('31', snapshot_data.get('71')))
                snapshot_data_dict = hp.update_current_market_data(snapshot_data)

                logging.info('{current_time} Running Bollinger with close price {current_close}.....'.format(
                    current_time=hp.get_datetime_obj_in_str(),
                    current_close=current_close
                    )
                )

                if first_add_flag:
                    market_data_list.append(snapshot_data_dict)
                    first_add_flag = False
                else:
                    market_data_list = market_data_list[:-1]
                    market_data_list.append(snapshot_data_dict)

                bolinger_frame = hp.get_bollinger_band(market_data_list, args.period, args.upper, args.lower, plot=False)
                side, b_upper, b_lower = hp.get_signal_for_last_frame(bolinger_frame, current_close)

                if side != 'NAN':
                    order_status = place_order_with_bollinger_band(stock_obj, account_id, conid, side, current_close)

                    logging.info("{current_time} {side} took place against with Bollinger Upper {upper} Close {close} Lower {lower}".format(
                        current_time=hp.get_datetime_obj_in_str(),
                        side=side,
                        upper=b_upper,
                        close=current_close,
                        lower=b_lower
                        )
                    )
                else:
                    logging.info("{current_time} Current Close does not cross Bollinger Upper {} Close {} Lower {}".format(
                        current_time=hp.get_datetime_obj_in_str(),
                        upper=b_upper,
                        close=current_close,
                        lower=b_lower
                        )
                    )

            current_market_data = stock_obj.get_current_market_data_snapshot(conid, flag=False)

            logging.info('{current_time} Going to take nap for {nap}s....'.format(
                current_time=hp.get_datetime_obj_in_str(),
                nap=NAP_SLEEP
                )
            )
            time.sleep(NAP_SLEEP)

    else:
        logging.info('{current_time} Market data snapshot history empty.'.format(
            current_time=hp.get_datetime_obj_in_str(),
            )
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Buy or Sell stock with Interactive Brokers.')
    parser.add_argument('--username', required=True, help='YOUR_USERNAME')
    parser.add_argument('--account-id', required=True, help='YOUR_ACCOUNT_NUMBER')
    parser.add_argument('--conid', required=True, type=int, help='STOCK_CONTRACT_ID')
    parser.add_argument('--passkey', help='YOUR_PASSWORD')
    parser.add_argument('--time-period', default='93d', help='Time period for Market Data')
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
