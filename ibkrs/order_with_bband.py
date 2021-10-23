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

def place_order_with_bollinger_band(stock_obj, account_id, conid, time_period, bar, period, upper, lower):

    market_data_list = stock_obj.get_market_data_history_list(conid, time_period, bar)


    if market_data_list:
        stock_obj.ib_client.unsubscribe_all_market_data_history()
        
        current_time_stamp_ms = hp.get_current_time_in_ms()

        str_conid = '{}'.format(conid)
        conids = [str_conid]
        fields = ['30', '70', '71']
        current_market_data = stock_obj.ib_client.market_data(conids, current_time_stamp_ms, fields)

        if current_market_data:
            current_market_data_dict = current_market_data[0]
            close_price = hp.convert_str_into_number(current_market_data_dict.get('31', 0))
            current_market_data_dict = hp.update_current_market_data(current_market_data_dict)

        if close_price:
            market_data_list.append(current_market_data_dict)
            bolinger_frame = hp.get_bollinger_band(market_data_list, period, upper, lower, plot=True)
            side = hp.get_signal_for_last_frame(bolinger_frame, close_price)

            order_status = {}
            quantity = 0

            if side == 'NAN':
                return order_status, side

            elif side == 'SELL': # SELL
                stock_postion = stock_obj.search_stock_by_conid(account_id, conid)

                if stock_postion:
                    quantity = stock_postion.get('position', 0)

            else: # BUY
                # get balance and calculate number of position to buy
                balance_type = 'AVB'
                account_balance_dict = stock_obj.get_account_balance(account_id, balance_type)
                account_balance = account_balance_dict.get('amount', 0)
                quantity = account_balance // current_close

            order_dict = {
                "secType": "secType = {}:STK".format(conid),
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
                "acctId": account_id,
                "conid": conid,
                "side": side,
                "cOID": "OID-{}".format(random.randint(1,1000))
            }

            orders = {"orders" : [order_dict]}
            order_status = stock_obj.place_order_stock(ACCOUNT, orders)
            
            return order_status, side



def main(ib_client, args):

    stock_obj = Stock(ib_client)

    market_data_list = stock_obj.get_market_data_history_list(args.conid, args.time_period, args.bar)


    if market_data_list:
        stock_obj.ib_client.unsubscribe_all_market_data_history()
        
        current_time_stamp_ms = hp.get_current_time_in_ms()

        str_conid = '{}'.format(args.conid)
        conids = [str_conid]
        fields = ['30', '70', '71']
        current_market_data = stock_obj.ib_client.market_data(conids, current_time_stamp_ms, fields)

        if current_market_data:
            current_market_data_dict = current_market_data[0]
            close_price = hp.convert_str_into_number(current_market_data_dict.get('31', 0))
            current_market_data_dict = hp.update_current_market_data(current_market_data_dict)

        if close_price:
            market_data_list.append(current_market_data_dict)
            bolinger_frame = hp.get_bollinger_band(market_data_list, args.period, args.upper, args.lower, plot=True)
            side = hp.get_signal_for_last_frame(bolinger_frame, close_price)

            order_status = {}
            quantity = 0

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
