import sys
sys.path.append('/home/ec2-user/pcv')

import argparse

from pprint import pprint
from ibw.client import IBClient
from ibkrs.stocks import Stock
from utils import helper

def main(stock_type='0'):

    config = helper.read_config()

    # Create a new session of the IB Web API.
    ib_client = IBClient(
        username=config.get('main','regular_username'),
        account=config.get('main','regular_account'),
        is_server_running=True
    )

    # Create an instance of Stock class
    stock = Stock(ib_client)

    # Grab stock list by type
    all_stocks = stock.get_stock_list(
        account_id=config.get('main','regular_account'),
        page_id='0',
        stock_type=stock_type
    )

    headers = ['STOCKS', 'PNL', 'Currency']

    dash_length = 35
    dash_header = "-" * dash_length

    print(dash_header)
    print("{}    {}    {}  ".format(headers[0], headers[1], headers[2]))
    print(dash_header)

    for row in all_stocks:
        stock, price, currency = row
        row = '{}    {}    {}'.format(stock, price, currency)
        print(row)

    print(dash_header)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Print avaiable stock with Interactive Brokers.')
    parser.add_argument('--stock-type', default='0', help='Stock type (default: 0, Avaiable: 1, -1)')
    args = parser.parse_args()


    main(args.stock_type)
