import sys
sys.path.append('/home/ec2-user/pcv')

import argparse
import random

from pprint import pprint
from ibw.client import IBClient
from stock_config import ORDERS



def sell_stock(args):

    # Create a new session of the IB Web API.
    ib_client = IBClient(
        username=args.username,
        account=args.account_id,
        is_server_running=True
    )

    # Update ORDERS dictionary

    ORDERS['acctId'] = args.account_id
    ORDERS['conid'] = args.conid
    ORDERS['side'] = args.side

    ORDERS['cOID'] = '{}-{}-{}'.format(args.account_id, args.conid, random.randint(1,1000))
    ORDERS['secType'] = 'secType = {}:STK'.format(args.conid)

    if args.coid:
        ORDERS['cOID'] = args.coid

    if args.sec_type:
        ORDERS['secType'] = args.sec_type

    if args.order_type:
        ORDERS['orderType'] = args.order_type

    if args.quantity:
        ORDERS['quantity'] = args.quantity

    if args.listing_exchange:
        ORDERS['listingExchange'] = args.listing_exchange

    if args.is_single_group:
        ORDERS['isSingleGroup'] = args.is_single_group

    if args.outside_rth:
        ORDERS['outsideRTH'] = args.outside_rth

    if args.price:
        ORDERS['price'] = args.price

    if args.referrer:
        ORDERS['referrer'] = args.referrer

    if args.use_adaptive:
        ORDERS['useAdaptive'] = args.use_adaptive

    if args.allocation_method:
        ORDERS['allocationMethod'] = args.allocation_method

    if args.tif:
        ORDERS['tif'] = args.tif

    print(ORDERS)
    # Grab stock list by type
    order_response = ib_client.place_orders(
        account_id=args.account_id,
        orders=[ORDERS]
    )
    print(order_response)

    


def main(args):
    sell_stock(args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Buy or Sell stock with Interactive Brokers.')
    parser.add_argument('--username', help='YOUR_USERNAME')
    parser.add_argument('--account-id', help='YOUR_ACCOUNT_NUMBER')
    parser.add_argument('--conid', help='STOCK_CONTRACT_ID')
    parser.add_argument('--side', help='SELL/BUY')
    parser.add_argument('--ticker', help='YOUR_STOCK_SYMBOL')
    parser.add_argument('--quantity', default=1, type=float, help='Quantity')
    parser.add_argument('--coid', default='{account-id}-{stock-id}-{any-interger}', help='Quantity')
    parser.add_argument('--order-type', default='MKT', help='Available : MKT, LMT, STP, STOP_LIMIT , MIDPRICE')
    parser.add_argument('--sec-type', default='secType = STOCK_CONTRACT_ID:STK', help='SEC_TYPE')
    parser.add_argument('--listing-exchange', default='SMART', help='valid_exchange: e.g: SMART,AMEX,NYSE,CBOE,...ETC')
    parser.add_argument('--is-single-group', default='True', help='True/False')
    parser.add_argument('--outside-rth', default='False', help='True/False')
    parser.add_argument('--price', default=0, type=float, help='optional if order is LMT, or STOP_LIMIT, this is the limit price.' +\
'For STP this is the stop price. For MIDPRICE this is the option price cap.')
    parser.add_argument('--tif', default='DAY', help='Time in Force. Values are DAY, IOC, GTC, OPG')
    parser.add_argument('--referrer', default='QuickTrade', help='Custom Order reference')
    parser.add_argument('--use-adaptive', default='True', help='True/False')
    parser.add_argument('--allocation-method', default='AvailableEquity', help='Available: NetLiquidity, AvailableEquity, EqualQuantity, PctChange')

    args = parser.parse_args()

    main(args)
