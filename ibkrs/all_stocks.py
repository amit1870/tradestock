import argparse
import logging
from requests.exceptions import HTTPError
from ibw.client import IBClient
from utils import helper as hp

logging.basicConfig(
    filename='app.log',
    format='%(levelname)s - %(name)s - %(message)s',
    level=logging.DEBUG
)

HEADERS     = ['AccountID', 'STOCKS', 'ContractID', 'PNL', 'PF/LS', 'Position', 'Currency']
BUFFER      = 1
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


def print_stock(ib_client, account_id, stock_type='0'):

    # grab account portfolios
    try:    
        account_positions = ib_client.portfolio_account_positions(
            account_id=account_id,
            page_id=0
        )
    except HTTPError as e:
        account_positions = []

    stock_list = []
    negative_stock_list = []
    profitable_stock_list = []
    max_length_symbol = max_length_pnl = max_length_currency = 0
    max_length_position = max_length_contractid = max_length_account_id = 0
    max_length_ps_ls = 5
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
                account_id = val
                len_of_stock_account_id = len(str(account_id))
                if max_length_account_id < len_of_stock_account_id:
                    max_length_account_id = len_of_stock_account_id


        values = (account_id, stock, contractid, pnl, position, currency)

        stock_list.append(values)

        if pnl < ZERO:
            negative_stock_list.append(values)
        elif pnl > ZERO:
            profitable_stock_list.append(values)

    print(DASH_HEADER)
    print("{}{}{}{}{}{}{}{}{}{}{}{}".format(HEADERS[0],
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
                                            HEADERS[6]))
    print(DASH_HEADER)

    if stock_type == NEGATIVE:
        selected_stock_list = negative_stock_list
    elif stock_type == POSITIVE:
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

        row = '{}{}{}{}{}{}{}{}{}{}{}{}'.format(acc_id,
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
                                                currency)
        print(row)

    print(DASH_HEADER)

def main(ib_client, args):
    account_id = args.account_id
    stock_type = '0'
    if args.stock_type:
        stock_type = args.stock_type
    print_stock(ib_client, account_id, stock_type)


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
    if args.passkey:
        ib_client = hp.authenticate_ib_client(ib_client, [args.username], [args.passkey])

    main(ib_client, args)
