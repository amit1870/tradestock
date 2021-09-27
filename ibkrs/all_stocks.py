import argparse

from requests.exceptions import HTTPError
from ibw.client import IBClient
from utils.auto_mode import auto_mode_on_accounts
from utils import helper as hp


HEADERS     = ['AccountID', 'STOCKS', 'ContractID', 'PNL', 'PF/LS', 'Position', 'Currency']
DASH_LENGTH = 62   # Dash length
DASH_HEADER = "-" * DASH_LENGTH
PROFIT      = 'PF'
LOSS        = 'LS'
ZERO        = 0
NEGATIVE    = '-1'
POSITIVE    = '1'

def print_stock(ib_client, args):

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
            if key == 'acctId':
                account_id = val

        values = (account_id, stock, contractid, pnl, position, currency)

        stock_list.append(values)

        if pnl < ZERO:
            negative_stock_list.append(values)
        elif pnl > ZERO:
            profitable_stock_list.append(values)

    print(DASH_HEADER)
    print("{}    {}    {}    {}  {}    {}  ".format(HEADERS[0],
                                                    HEADERS[1],
                                                    HEADERS[2],
                                                    HEADERS[3],
                                                    HEADERS[4], HEADERS[5], HEADERS[6]))
    print(DASH_HEADER)

    if args.stock_type == NEGATIVE:
        selected_stock_list = negative_stock_list
    elif args.stock_type == POSITIVE:
        selected_stock_list = profitable_stock_list
    else:
        selected_stock_list = stock_list

    for row in selected_stock_list:
        acc_id, name, conid, pnl, position, currency = row

        profit_or_loss = ZERO
        if pnl < 0:
            profit_or_loss = LOSS
        elif pnl > 0:
            profit_or_loss = PROFIT

        row = '{}    {}    {}    {}    {}    {}    {}  '.format(acc_id,
                                                                name,
                                                                conid,
                                                                pnl,
                                                                profit_or_loss,
                                                                position, currency)
        print(row)

    print(DASH_HEADER)

def print_blank_stock():
    print(DASH_HEADER)
    print("{}    {}    {}    {}  {}    {}  ".format(HEADERS[0],
                                                    HEADERS[1],
                                                    HEADERS[2],
                                                    HEADERS[3],
                                                    HEADERS[4], HEADERS[5], HEADERS[6]))
    print(DASH_HEADER)
    print(DASH_HEADER)

def main(args):
    # Create a new session of the IB Web API.
    ib_client = IBClient(
        username=args.username,
        account=args.account_id,
        is_server_running=True
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
                with hp.silent_std_out():
                    ib_client.logout()
            except HTTPError as e:
                pass

            authenticated_accounts = auto_mode_on_accounts(usernames, passwords, sleep_sec=1)

            if authenticated_accounts:
                auth_response = ib_client.is_authenticated()

                # Finally make sure we are authenticated.
                if 'authenticated' in auth_response.keys() and auth_response['authenticated']:
                    authenticated = True

        if authenticated:
            print_stock(ib_client, args)
        else:
            print_blank_stock()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Print avaiable stock with Interactive Brokers.')
    parser.add_argument('--username', required=True, help='YOUR_USERNAME')
    parser.add_argument('--passkey', help='YOUR_PASSWORD')
    parser.add_argument('--account-id', required=True, help='YOUR_ACCOUNT_NUMBER')
    parser.add_argument('--stock-type', default='0', help='Stock type (default: 0, Avaiable: 1, -1)')
    args = parser.parse_args()

    main(args)
