import argparse

from requests.exceptions import HTTPError
from pprint import pprint
from ibw.client import IBClient
from utils.auto_mode import auto_mode_on_accounts
from utils import helper as hp

def print_stock(ib_client, args):

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

def print_blank_stock(conid_or_symbol):
    print("{} cannot be searched. Please check account details.".format(conid_or_symbol))

def main(args):
    # Create a new session of the IB Web API.
    ib_client = IBClient(
        username=args.username,
        account=args.account_id,
        is_server_running=True
    )
    # Log the IB Client.
    logging.debug('Created IB client: {ib_client}'.format(
            ib_client=ib_client
        )
    )

    if args.passkey is None:
        print_stock(ib_client, args)
    else:
        # try to connect once
        usernames = [args.username]
        passwords = [args.passkey]
        authenticated = False
        if usernames and passwords:
            # logout if any existing session
            try:
                ib_client.logout()
            except HTTPError as e:
                pass

            authenticated_accounts = auto_mode_on_accounts(usernames, passwords, sleep_sec=2)

            logging.debug('Authenticated account by auto mode: {authenticated_accounts}'.format(
                    authenticated_accounts=authenticated_accounts
                )
            )
            try:
                if authenticated_accounts:
                    auth_response = ib_client.is_authenticated()
                    logging.debug('Auth Response: {auth_response}'.format(
                            auth_response=auth_response
                        )
                    )
                    # Finally make sure we are authenticated.
                    if 'authenticated' in auth_response.keys() and auth_response['authenticated']:
                        authenticated = True

            except HTTPError as e:
                logging.debug('Auth Error: {auth_error}'.format(
                            auth_error=e
                        )
                    )
                pass

        if authenticated:
            print_stock(ib_client, args)
        else:
            print_blank_stock(args.conid_or_symbol)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get stock details with Interactive Brokers.')
    parser.add_argument('--username', required=True, help='YOUR_USERNAME')
    parser.add_argument('--passkey', help='YOUR_PASSWORD')
    parser.add_argument('--account-id', required=True, help='YOUR_ACCOUNT_NUMBER')
    parser.add_argument('--conid-or-symbol', help='Give contract id or symbol')
    args = parser.parse_args()

    main(args)
