import sys
import argparse
import logging

from requests.exceptions import HTTPError
from pprint import pprint
from ibw.client import IBClient
from ibw.stock import Stock
from utils import helper as hp

def get_account_balance(stock_obj, account_id, balance_type='AVB'):

    # Get account balance
    account_balance_dict = stock_obj.get_account_balance(account_id, balance_type)
    account_balance = account_balance_dict.get('amount', 0)

    return account_balance

def main(ib_client, args):
    stock_obj = Stock(ib_client)
    balance = get_account_balance(stock_obj, args.account_id)
    print('Username ',args.username, end=' | ')
    print('AccountID ',args.account_id, end=' | ')
    print('Balance ', balance, end=' | \n')

    selected_account = stock_obj.ib_client.server_accounts()
    print(selected_account)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get stock details with Interactive Brokers.')
    parser.add_argument('--username', required=True, help='YOUR_USERNAME')
    parser.add_argument('--passkey', help='YOUR_PASSWORD')
    parser.add_argument('--account-id', required=True, help='YOUR_ACCOUNT_NUMBER')
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
