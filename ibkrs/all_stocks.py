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

    # grab account portfolios
    stock = Stock(ib_client)

    all_stocks = stock.get_stock_list(account_id=config.get('main','regular_account'), page_id='0')

    headers = ['STOCKS', 'PNL', 'Currency']

    dash_length = 35
    margin_length = 4
    headers_length = 0

    dash_header = "-" * dash_length

    for header in headers[:-1]:
        headers_length = headers_length + len(header)

    space_length = dash_length - headers_length

    print(dash_header)
    print("{}{}{}    {}".format(headers[0]," " * space_length , headers[1]), headers[2])
    print(dash_header)

    for row in all_stocks:
        stock, price, currency = row
        stock_length = len(stock)
        spaces = " " * ( space_length + len(headers[0]) - stock_length)
        row = '{}{}{}    {}'.format(stock, spaces, profit, currency)
        print(row)

    print(dash_header)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Print avaiable stock with Interactive Brokers.')
    parser.add_argument('--stock-type', default='0', help='Stock type (default: 0, Avaiable: 1, -1)')
    args = parser.parse_args()


    main(args.stock_type)





