import sys
import argparse

from pprint import pprint
from ibw.client import IBClient
from utils import helper as hp
from stock import Stock


def main(ib_client, args):

    stock_obj = Stock(ib_client)
    
    if args.conid:
        pprint(stock_obj.search_stock_by_conid(args.account_id, args.conid))

    elif args.symbol:
        pprint(stock_obj.search_stock_by_symbol(args.symbol))

    else:
        pprint(stock_obj.ib_client.portfolio_account_info(args.account_id))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get stock details with Interactive Brokers.')
    parser.add_argument('--username', required=True, help='YOUR_USERNAME')
    parser.add_argument('--passkey', help='YOUR_PASSWORD')
    parser.add_argument('--account-id', required=True, help='YOUR_ACCOUNT_NUMBER')
    parser.add_argument('--conid', help='Give contract symbol')
    parser.add_argument('--symbol', help='Give contract symbol')
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

