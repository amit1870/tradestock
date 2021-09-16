import sys
sys.path.append('/home/ec2-user/pcv')

import argparse

from pprint import pprint
from ibw.client import IBClient

def print_stock(args):

    # Create a new session of the IB Web API.
    ib_client = IBClient(
        username=args.username,
        account=args.account_id,
        is_server_running=True
    )

    # Grab the Specific Postion in a Portfolio.
    portfolio_position = ib_client.portfolio_account_position(
        account_id=args.account_id,
        conid=args.conid
    )
    pprint(portfolio_position)



def main(args):
    print_stock(args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get stock details with Interactive Brokers.')
    parser.add_argument('--username', help='YOUR_USERNAME')
    parser.add_argument('--account-id', help='YOUR_ACCOUNT_NUMBER')
    parser.add_argument('--conid', help='Give contract id')
    args = parser.parse_args()

    main(args)
