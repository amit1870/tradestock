import sys
sys.path.append('/home/ec2-user/pcv')

import argparse

from pprint import pprint
from ibw.client import IBClient
from utils import helper

def print_stock(contact_id):
    config = helper.read_config()

    # Create a new session of the IB Web API.
    ib_client = IBClient(
        username=config.get('main','regular_username'),
        account=config.get('main','regular_account'),
        is_server_running=True
    )

    # Grab the Specific Postion in a Portfolio.
    portfolio_position = ib_client.portfolio_account_position(
        account_id=config.get('main','regular_account'),
        conid=contact_id
    )
    pprint(portfolio_position)



def main(contact_id):
    print_stock(contact_id)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Print avaiable stock with Interactive Brokers.')
    parser.add_argument('--conid', help='Give contract id')
    args = parser.parse_args()

    main(args.conid)
