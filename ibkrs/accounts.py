import argparse
import logging

from requests.exceptions import HTTPError
from pprint import pprint
from ibw.client import IBClient
from utils import helper as hp

def portfolio_account_summary(ib_client, account_id):

    # Grab the Specific Postion in a Portfolio.
    try:    
        account_summary = ib_client.portfolio_account_summary(
            account_id=account_id,
        )
    except HTTPError as e:
        account_summary = []

    return account_summary

def main(ib_client, args):
    print(portfolio_account_summary(ib_client, args.account_id))
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get stock details with Interactive Brokers.')
    parser.add_argument('--username', required=True, help='YOUR_USERNAME')
    parser.add_argument('--passkey', help='YOUR_PASSWORD')
    parser.add_argument('--account-id', required=True, help='YOUR_ACCOUNT_NUMBER')
    parser.add_argument('--conid-or-symbol', help='Give contract id or symbol')
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

    if not args.passkey:
        main(ib_client, args)
    elif auth_status:
        main(ib_client, args)
