import argparse
import logging

from requests.exceptions import HTTPError
from pprint import pprint
from ibw.client import IBClient
from utils import helper as hp

class Stock(object):
    def __init__(self, ib_client):
        self.ib_client = ib_client

    def search_stock_by_symbol(self, symbol):
        try:
            search_result = self.ib_client.symbol_search(symbol=symbol)
        except HTTPError as e:
            search_result = []

        return search_result

    def search_stock_by_conid(self, account_id, contract_id):
        try:
            portfolio_position = self.ib_client.portfolio_account_position(
                account_id=account_id,
                conid=contract_id
            )
        except HTTPError as e:
            portfolio_position = []

        return portfolio_position

    def portfolio_account_summary(self, account_id):

        # Grab the Specific Postion in a Portfolio.
        try:    
            account_summary = self.ib_client.portfolio_account_summary(
                account_id=account_id,
            )
        except HTTPError as e:
            account_summary = {}

        return account_summary

    def get_account_balance(self, account_id, balance_type):
        BAL_TYPES = {
            'AVB': 'availablefunds'
        }
        # Grab the balance by its balance type from account summary.
        try:    
            account_balance_summary = self.ib_client.portfolio_account_summary(
                account_id=account_id,
            )
        except HTTPError as e:
            account_summary = {}

        return account_summary.get(BAL_TYPES.get(balance_type,'AVB')) if account_summary else account_summary

    def place_order_stock(self, account_id, order_list):
        order_status = {}

        order_response = self.ib_client.place_orders(
            account_id=account_id,
            orders=order_list
        )

        if order_response:
            response_id_dict = order_response[0]
            reply_id = response_id_dict.get('id', None)

            if reply_id is not None:
                confirm = True
                reply_response = self.ib_client.place_order_reply(
                    reply_id=reply_id,
                    reply=confirm)
                order_status = reply_response

        return order_status

    def place_order_stock_with_confirm(self, account_id, orders_list):
        order_status = {}

        proceed = 'Yes'
        proceed = input("Do you want to place order? Yes/No(Yes):")
        proceed = proceed.strip()
        if proceed == '':
            proceed = 'Yes'

        proceed = proceed.upper()

        if proceed == 'YES' or proceed == 'Y':
            # Place Order
            order_response = self.ib_client.place_orders(
                account_id=account_id,
                orders=order_dict
            )
            order_status = order_response

        if order_status:
            response_id_dict = order_response[0]
            reply_id = response_id_dict.get('id')

            proceed = input("Do you want to confirm order id {}? Yes/No(Yes):".format(reply_id))
            proceed = proceed.strip()
            if proceed == '':
                proceed = 'Yes'

            proceed = proceed.upper()

            if proceed == 'YES' or proceed == 'Y':
                reply_response = self.ib_client.place_order_reply(
                    reply_id=reply_id,
                    reply=True)

                order_status = reply_response

        return order_status


def main(ib_client, args):

    stock_obj = Stock(ib_client)

    if args.conid:
        pprint(stock_obj.search_stock_by_conid(args.account_id, args.conid))

    elif args.symbol:
        pprint(stock_obj.search_stock_by_symbol(args.symbol))

    else:
        pprint(stock_obj.portfolio_account_summary(args.account_id))

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

    if not args.passkey:
        main(ib_client, args)
    elif auth_status:
        main(ib_client, args)

