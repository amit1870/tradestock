import sys
import argparse
sys.path.append('/home/ec2-user/virenv/pcv')

from requests.exceptions import HTTPError
from ibw.client import IBClient

def print_stock(args):

    # Create a new session of the IB Web API.
    ib_client = IBClient(
        username=args.username,
        account=args.account_id,
        is_server_running=True
    )

    # grab account portfolios
    try:    
        account_positions = ib_client.portfolio_account_positions(
            account_id=args.account_id,
            page_id=0
        )
    except HTTPError as e:
        account_positions = []

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
            if key == 'conid':
                contractid = val

        values = (stock, contractid, pnl, position, currency)

        stock_list.append(values)

        if pnl < 0 :
            negative_stock_list.append(values)
        elif pnl > 0:
            profitable_stock_list.append(values)

    headers = ['STOCKS', 'ContractID', 'P/L', 'PNL', 'Position', 'Currency']

    dash_length = 55
    dash_header = "-" * dash_length

    print(dash_header)
    print("{}    {}    {}  {}    {}  ".format(headers[0], headers[1], headers[2], headers[3], headers[4], headers[5]))
    print(dash_header)

    profit_or_loss = None
    if args.stock_type == '-1':
        selected_stock_list = negative_stock_list
        profit_or_loss = 'LOSS'
    elif args.stock_type == '1':
        selected_stock_list = profitable_stock_list
        profit_or_loss = 'PROFIT'
    else:
        selected_stock_list = stock_list

    for row in selected_stock_list:
        name, conid, pnl, position, currency = row
        if profit_or_loss is None:
            if pnl < 0:
                profit_or_loss = 'LOSS'
            elif pnl > 0:
                profit_or_loss = 'PROFIT'
            else:
                profit_or_loss = 'ZERO'

        row = '{}    {}    {}    {}    {}    {}  '.format(name, conid, pnl, profit_or_loss, position, currency)
        print(row)

    print(dash_header)


def main(args):
    print_stock(args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Print avaiable stock with Interactive Brokers.')
    parser.add_argument('--username', help='YOUR_USERNAME')
    parser.add_argument('--account-id', help='YOUR_ACCOUNT_NUMBER')
    parser.add_argument('--stock-type', default='0', help='Stock type (default: 0, Avaiable: 1, -1)')
    args = parser.parse_args()

    main(args)
