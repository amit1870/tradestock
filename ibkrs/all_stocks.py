import sys
sys.path.append('/home/ec2-user/peace_haven')

from pprint import pprint
from ibw.client import IBClient
from utils import helper


config = helper.read_config()

# Create a new session of the IB Web API.
ib_client = IBClient(
    username=config.get('main','regular_username'),
    account=config.get('main','regular_account'),
    is_server_running=True
)

# grab account portfolios
account_positions = ib_client.portfolio_account_positions(
    account_id=config.get('main','regular_account'),
    page_id=0
)

dash_length = 25

dash_header = "-" * dash_length

headers = ['STOCKS', 'PNL']

space_length = dash_length - len(headers[0]) - len(headers[1]) - 6

print(dash_header)
print("{}{}{}".format(headers[0]," " * space_length , headers[1]))
print(dash_header)

for row in account_positions:
    for key, val in row.items():
        if key == 'contractDesc':
            stock = val
        if key == 'unrealizedPnl':
            profit = val
    stock_length = len(stock)
    spaces = " " * ( space_length + len(headers[0]) - stock_length)
    row = '{}{}{}'.format(stock, spaces, profit)
    print(row)

print(dash_header)

