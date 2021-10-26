import sys
import argparse

from pprint import pprint
from ibw.client import IBClient
from utils import helper as hp
from stock import Stock


def main(ib_client, args):

    stock_obj = Stock(ib_client)
    stock_obj.get_current_market_data_snapshot(args.conid)

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

