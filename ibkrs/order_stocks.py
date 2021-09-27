import argparse
import random

from pprint import pprint
from ibw.client import IBClient
from utils.auto_mode import auto_mode_on_accounts
from utils import helper as hp
from stock_config import ORDERS

def place_order_stock(ib_client, args):
    # Update ORDERS dictionary
    ORDERS['acctId'] = args.account_id
    ORDERS['conid'] = args.conid
    ORDERS['side'] = args.side
    ORDERS['cOID'] = args.coid
    ORDERS['secType'] = args.sec_type
    ORDERS['ticker'] = args.ticker

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

    
    order_dict = {"orders" : [ORDERS]}
    print()
    print("Place Order details:")
    pprint(order_dict)
    print()

    proceed = input("Do you want to place order? Yes/No(Yes):")
    proceed = proceed.upper()

    if proceed == '':
        proceed = 'Y'

    if proceed == 'YES' or proceed == 'Y':
        # Grab stock list by type
        order_response = ib_client.place_orders(
            account_id=args.account_id,
            orders=order_dict
        )
        print("Place Order Response:")
        pprint(order_response)
        print()


        if order_response:
            response_id_dict = order_response[0]
            reply_id = response_id_dict.get('id', None)

            if reply_id is not None:
                confirmation = input("Confirm place order in Yes/No(Yes):")
                confirmation = confirmation.upper()

                if confirmation == '':
                    confirmation = 'Y'
                if confirmation == 'YES' or confirmation == 'Y':
                    confirmation = True
                else:
                    confirmation = False

                if confirmation:
                    reply = {'confirmed' : confirmation}
                    reply_response = ib_client.place_order_reply(
                        reply_id=reply_id,
                        reply=confirmation)

                    print("Place Order Reply Response:")
                    pprint(reply_response)
                    print()
                    print("Order has been placed successfully.")
                else:
                    print("Cancelled Place Order Reply.")
                print()
    else:
        print("Cancelled Place Order.")

def failed_place_order_stock():
    print("Order cannot be placed. Please check account details.")

def main(args):
    # Create a new session of the IB Web API.
    ib_client = IBClient(
        username=args.username,
        account=args.account_id,
        is_server_running=True
    )

    if args.passkey is None:
        place_order_stock(ib_client, args)
    else:
        # try to connect once
        usernames = [args.username]
        passwords = [args.passkey]
        authenticated = False
        if usernames and passwords:
            # logout if any existing session
            try:
                with hp.silent_std_out():
                    ib_client.logout()
            except HTTPError as e:
                pass

            authenticated_accounts = auto_mode_on_accounts(usernames, passwords, sleep_sec=1)

            if authenticated_accounts:
                auth_response = ib_client.is_authenticated()

                # Finally make sure we are authenticated.
                if 'authenticated' in auth_response.keys() and auth_response['authenticated']:
                    authenticated = True

        if authenticated:
            place_order_stock(ib_client, args)
        else:
            failed_place_order_stock()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Buy or Sell stock with Interactive Brokers.')
    parser.add_argument('--username', required=True, help='YOUR_USERNAME')
    parser.add_argument('--passkey', help='YOUR_PASSWORD')
    parser.add_argument('--account-id', required=True, help='YOUR_ACCOUNT_NUMBER')

    parser.add_argument('--conid', type=int, help='STOCK_CONTRACT_ID')
    parser.add_argument('--side', help='SELL/BUY')
    parser.add_argument('--sec-type', help='secType = conid:security_type')
    parser.add_argument('--coid', help='Customer Order ID')
    parser.add_argument('--ticker', help='YOUR_STOCK_SYMBOL')

    parser.add_argument('--order-type', default="MKT", help='Available : MKT, LMT, STP, STOP_LIMIT , MIDPRICE')
    parser.add_argument('--quantity', default=1, type=float, help='Quantity')
    parser.add_argument('--listing-exchange', default="SMART", help='valid_exchange: e.g: SMART,AMEX,NYSE,CBOE,...ETC')
    parser.add_argument('--is-single-group', default=True, help='True/False')
    parser.add_argument('--outside-rth', default=False, help='True/False')
    parser.add_argument('--price', default=0, type=float, help='optional if order is LMT, or STOP_LIMIT, this is the limit price.' +\
'For STP this is the stop price. For MIDPRICE this is the option price cap.')
    parser.add_argument('--tif', default="DAY", help='Time in Force. Values are DAY, IOC, GTC, OPG')
    parser.add_argument('--referrer', default="QuickTrade", help='Custom Order reference')
    parser.add_argument('--use-adaptive', default=True, help='True/False')
    parser.add_argument('--allocation-method', default="AvailableEquity", help='Available: NetLiquidity, AvailableEquity, EqualQuantity, PctChange')

    args = parser.parse_args()

    main(args)
