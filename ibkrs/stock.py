import sys
import argparse
sys.path.append('/home/ec2-user/virenv/pcv')

from requests.exceptions import HTTPError
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
    contract_id_flag = False
    try:
        contract_id = int(args.conid_or_symbol)
        contract_id_flag = True
    except ValueError as e:
        symbol = args.conid_or_symbol

    try:
        if contract_id_flag:
            portfolio_position = ib_client.portfolio_account_position(
                account_id=args.account_id,
                conid=contract_id
            )
            
        else:
            portfolio_position = ib_client.symbol_search(symbol=symbol)
    except HTTPError as e:
        portfolio_position = "{} does not found.".format(args.conid_or_symbol)

    pprint(portfolio_position)



def main(args):
    print_stock(args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get stock details with Interactive Brokers.')
    parser.add_argument('--username', help='YOUR_USERNAME')
    parser.add_argument('--account-id', help='YOUR_ACCOUNT_NUMBER')
    parser.add_argument('--conid-or-symbol', help='Give contract id or symbol')
    args = parser.parse_args()

    main(args)
