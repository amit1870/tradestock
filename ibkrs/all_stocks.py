import sys
sys.path.append('/home/ec2-user/pcv')

import argparse

from pprint import pprint
from ibw.client import IBClient
from utils import helper

def print_stock(stock_type='0'):
    config = helper.read_config()

    # Create a new session of the IB Web API.
    ib_client = IBClient(
        username=config.get('main','regular_username'),
        account=config.get('main','regular_account'),
        is_server_running=True
    )

    # grab account portfolios
    account_positions = ib_client.portfolio_account_positions(
        account_id=config.get('main','regular_account'),
        page_id=0
    )

    stock_list = []
    negative_stock_list = []
    profitable_stock_list = []
    for row in account_positions:
        for key, val in row.items():
            if key == 'contractDesc':
                stock = val
            if key == 'unrealizedPnl':
                pnl = val
            if key == 'currency':
                currency = val
            if key == 'position':
                position = val

        values = (stock, pnl, position, currency)

        stock_list.append(values)

        if pnl < 0 :
            negative_stock_list.append(values)
        elif pnl > 0:
            profitable_stock_list.append(values)

    headers = ['STOCKS', 'PNL', 'Position', 'Currency']

    dash_length = 40
    dash_header = "-" * dash_length

    print(dash_header)
    print("{}    {}    {}  {}  ".format(headers[0], headers[1], headers[2], headers[3]))
    print(dash_header)

    if stock_type == '-1':
        selected_stock_list = negative_stock_list
    elif stock_type == '1':
        selected_stock_list = profitable_stock_list
    else:
        selected_stock_list = stock_list

    for row in selected_stock_list:
        name, price, position, currency = row
        row = '{}    {}    {}    {} '.format(name, price, position, currency)
        print(row)

    print(dash_header)


def main(stock_type):
    print_stock(stock_type)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Print avaiable stock with Interactive Brokers.')
    parser.add_argument('--stock-type', default='0', help='Stock type (default: 0, Avaiable: 1, -1)')
    args = parser.parse_args()

    main(args.stock_type)
