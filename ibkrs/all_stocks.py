import sys
import argparse

from requests.exceptions import HTTPError

from ibw.client import IBClient
from stock import Stock
from utils import helper as hp


HEADERS     = ['Username', 'AccountID', 'STOCKS', 'ContractID', 'PNL', 'PF/LS', 'Position', 'Balance', 'Currency']
BUFFER      = 15
SPACE       = ' '
HEAD_SPACES = SPACE * 3
HEADERS_LEN = len(HEAD_SPACES.join(HEADERS)) + BUFFER
DASH_HEADER = "-" * HEADERS_LEN
PROFIT      = 'PF'
LOSS        = 'LS'
ZERO        = 0
NEGATIVE    = '-1'
POSITIVE    = '1'
SPACE_LEN   = 4
SPACES      = ' ' * SPACE_LEN


def print_stock(stock_obj, username, account_id, stock_type='0'):

    # grab account portfolios
    account_positions = stock_obj.get_account_positions_by_page_id(account_id, page_id=0)

    # Get account balance
    account_balance_dict = stock_obj.get_account_balance(account_id, balance_type='AVB')
    account_balance = account_balance_dict.get('amount', 0)
    account_balance = "{:.2f}".format(round(account_balance, 2))

    stock_list = []
    negative_stock_list = []
    profitable_stock_list = []
    max_length_symbol = max_length_pnl = max_length_currency = 0
    max_length_position = max_length_contractid = max_length_account_id = 0
    max_length_ps_ls = 5
    max_length_username = len(username)
    max_length_balance = len(str(account_balance))

    for row in account_positions:
        for key, val in row.items():
            if key == 'contractDesc':
                stock = val
                len_of_stock_symbol = len(str(stock))
                if max_length_symbol < len_of_stock_symbol:
                    max_length_symbol = len_of_stock_symbol

            if key == 'unrealizedPnl':
                pnl = val
                len_of_stock_pnl = len(str(pnl))
                if max_length_pnl < len_of_stock_pnl:
                    max_length_pnl = len_of_stock_pnl

            if key == 'currency':
                currency = val
                len_of_stock_currency = len(str(currency))
                if max_length_currency < len_of_stock_currency:
                    max_length_currency = len_of_stock_currency

            if key == 'position':
                position = val
                len_of_stock_position = len(str(position))
                if max_length_position < len_of_stock_position:
                    max_length_position = len_of_stock_position

            if key == 'conid':
                contractid = val
                len_of_stock_contractid = len(str(contractid))
                if max_length_contractid < len_of_stock_contractid:
                    max_length_contractid = len_of_stock_contractid

            if key == 'acctId':
                row_account_id = val
                len_of_stock_account_id = len(str(row_account_id))
                if max_length_account_id < len_of_stock_account_id:
                    max_length_account_id = len_of_stock_account_id

        if row_account_id == account_id:
            values = (username, row_account_id, stock, contractid, pnl, position, account_balance, currency)

            stock_list.append(values)

            if pnl < ZERO:
                negative_stock_list.append(values)
            elif pnl > ZERO:
                profitable_stock_list.append(values)

    print(DASH_HEADER)
    print("{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}".format(HEADERS[0],
                                                SPACES,                                    
                                                HEADERS[1],
                                                SPACES,
                                                HEADERS[2],
                                                SPACES,
                                                HEADERS[3],
                                                SPACES,
                                                HEADERS[4],
                                                SPACES,
                                                HEADERS[5],
                                                SPACES,
                                                HEADERS[6],
                                                SPACES,
                                                HEADERS[7],
                                                SPACES,
                                                HEADERS[8]))
    print(DASH_HEADER)

    if stock_type == NEGATIVE:
        selected_stock_list = negative_stock_list
    elif stock_type == POSITIVE:
        selected_stock_list = profitable_stock_list
    else:
        selected_stock_list = stock_list

    for row in selected_stock_list:
        uname, acc_id, name, conid, pnl, position, balance, currency = row

        profit_or_loss = ZERO
        if pnl < 0:
            profit_or_loss = LOSS
        elif pnl > 0:
            profit_or_loss = PROFIT

        row = '{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}'.format(uname,
                                                    SPACE * (max_length_username + SPACE_LEN - len(str(uname))),
                                                    acc_id,
                                                    SPACE * (max_length_account_id + SPACE_LEN - len(str(acc_id))),
                                                    name,
                                                    SPACE * (max_length_symbol + SPACE_LEN - len(str(name))),
                                                    conid,
                                                    SPACE * (max_length_contractid + SPACE_LEN - len(str(conid))),
                                                    pnl,
                                                    SPACE * (max_length_pnl + SPACE_LEN - len(str(pnl))),
                                                    profit_or_loss,
                                                    SPACE * (max_length_ps_ls + SPACE_LEN - len(str(profit_or_loss))),
                                                    position,
                                                    SPACE * (max_length_position + SPACE_LEN - len(str(position))),
                                                    balance,
                                                    SPACE * (max_length_balance + SPACE_LEN - len(str(max_length_balance))),
                                                    currency)
        print(row)

    print(DASH_HEADER)

def main(ib_client, args):

    stock_obj = Stock(ib_client)

    print_stock(stock_obj, args.username, args.account_id, args.stock_type)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Print avaiable stock with Interactive Brokers.')
    parser.add_argument('--username', required=True, help='YOUR_USERNAME')
    parser.add_argument('--passkey', help='YOUR_PASSWORD')
    parser.add_argument('--account-id', required=True, help='YOUR_ACCOUNT_NUMBER')
    parser.add_argument('--stock-type', default='0', help='Stock type (default: 0, Avaiable: 1, -1)')
    args = parser.parse_args()

    # Create a new session of the IB Web API.
    ib_client = IBClient(
        username=args.username,
        account=args.account_id,
        is_server_running=True
    )
    auth_status = False
    if args.passkey:
        ib_client, auth_status = hp.authenticate_ib_client(ib_client, [args.username], [args.passkey])


    main(ib_client, args)
