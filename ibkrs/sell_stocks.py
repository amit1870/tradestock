import sys
sys.path.append('/home/ec2-user/pcv')

import argparse

from pprint import pprint
from ibw.client import IBClient
from ibkrs.stocks import Stock
from utils import helper

import data
import json

r = data.orders_list
r = json.dumps(r)
r = json.loads(r)

config = helper.read_config()

# Create a new session of the IB Web API.
ib_client = IBClient(
    username=config.get('main','regular_username'),
    account=config.get('main','regular_account'),
    is_server_running=True
)

# Create an instance of Stock class
stock = Stock(ib_client)

def sell_stock(stock_type='0'):
    global stock, config, ib_client, r

    # Grab stock list by type
    all_stocks = stock.place_orders(
        account_id=config.get('main','regular_account'),
        orders=r
    )

    


def main(stock_type):
    sell_stock(stock_type)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Print avaiable stock with Interactive Brokers.')
    parser.add_argument('--stock-type', default='0', help='Stock type (default: 0, Avaiable: 1, -1)')
    args = parser.parse_args()

    main(args.stock_type)
