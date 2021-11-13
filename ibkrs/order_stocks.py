import sys
import argparse
import random
import logging
from pprint import pprint
from requests.exceptions import HTTPError

from ibw.client import IBClient
from ibw.stock import Stock
from utils import helper as hp

def main(ib_client, args):
    order_list = hp.prepare_order_dict_from_args(vars(args))
    print("Review Order Details: {}".format(order_list))

    stock_obj = Stock(ib_client)

    confirm = True
    if args.confirm == 'False':
        confirm = False

    order_status = stock_obj.place_order_stock(args.account_id, order_list, confirm=confirm)

    print("Order has taken place with message {}".format(order_status))



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Buy or Sell stock with Interactive Brokers.')
    parser.add_argument('--username', required=True, help='YOUR_USERNAME')
    parser.add_argument('--passkey', help='YOUR_PASSWORD')
    parser.add_argument('--account-id', required=True, help='YOUR_ACCOUNT_NUMBER')

    parser.add_argument('--conid', required=True, type=int, help='STOCK_CONTRACT_ID')
    parser.add_argument('--side', required=True, help='SELL/BUY')

    parser.add_argument('--sec-type', help='secType = conid:security_type')
    parser.add_argument('--coid', help='Customer Order ID')
    parser.add_argument('--ticker', help='YOUR_STOCK_SYMBOL')
    parser.add_argument('--confirm', help='Confirmation', default=True)
    parser.add_argument('--order-type', default="MKT", help='Available : MKT, LMT, STP, STOP_LIMIT , MIDPRICE')
    parser.add_argument('--quantity', default=1, type=float, help='Quantity')
    parser.add_argument('--listing-exchange', default="SMART", help='valid_exchange: e.g: SMART,AMEX,NYSE,CBOE,...ETC')
    parser.add_argument('--is-single-group', default=True, help='True/False')
    parser.add_argument('--outside-rth', default=False, help='True/False')
    parser.add_argument('--price', default=0, type=float, help='optional if order is LMT, or STOP_LIMIT, this is the limit price.')
    parser.add_argument('--tif', default="DAY", help='Time in Force. Values are DAY, IOC, GTC, OPG')
    parser.add_argument('--referrer', default="QuickTrade", help='Custom Order reference')
    parser.add_argument('--use-adaptive', default=True, help='True/False')
    parser.add_argument('--allocation-method', default="AvailableEquity", help='Available: NetLiquidity, AvailableEquity, EqualQuantity, PctChange')

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
