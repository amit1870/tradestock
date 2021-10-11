import argparse
import logging

from requests.exceptions import HTTPError
from pprint import pprint
from ibw.client import IBClient
from utils.auto_mode import auto_mode_on_accounts
from utils import helper as hp


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
                    ib_client.is_authenticated()
            except HTTPError as e:
                pass

        print_stock(ib_client, args)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get stock details with Interactive Brokers.')
    parser.add_argument('--username', required=True, help='YOUR_USERNAME')
    parser.add_argument('--passkey', help='YOUR_PASSWORD')
    parser.add_argument('--account-id', required=True, help='YOUR_ACCOUNT_NUMBER')
    parser.add_argument('--conid-or-symbol', help='Give contract id or symbol')
    args = parser.parse_args()

    main(args)
