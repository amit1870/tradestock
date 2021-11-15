import time

from datetime import datetime, timezone
from requests.exceptions import HTTPError

class Stock(object):
    def __init__(self, ib_client):
        self.ib_client = ib_client

    def search_stock_by_symbol(self, symbol):
        try:
            search_result = self.ib_client.symbol_search(symbol=symbol)
        except HTTPError as e:
            search_result = []

        return search_result

    def search_stock_by_conid(self, account_id, contract_id):
        try:
            portfolio_position = self.ib_client.portfolio_account_position(
                account_id=account_id,
                conid=contract_id
            )
        except HTTPError as e:
            portfolio_position = []

        return portfolio_position

    def get_account_positions_by_page_id(self, account_id, page_id=0):
        # grab account portfolios
        try:
            account_positions = self.ib_client.portfolio_account_positions(
                account_id=account_id,
                page_id=page_id
            )
        except HTTPError as e:
            account_positions = []

        return account_positions

    def portfolio_account_summary(self, account_id):

        # Grab the Specific Postion in a Portfolio.
        try:    
            account_summary = self.ib_client.portfolio_account_summary(
                account_id=account_id,
            )
        except HTTPError as e:
            account_summary = {}

        return account_summary

    def get_account_balance(self, account_id, balance_type):
        BAL_TYPES = {
            'AVB': 'availablefunds'
        }
        # Grab the balance by its balance type from account summary.
        try:    
            account_summary = self.ib_client.portfolio_account_summary(
                account_id=account_id,
            )
        except HTTPError as e:
            account_summary = {}

        return account_summary.get(BAL_TYPES.get(balance_type,'AVB')) if account_summary else account_summary


    def place_order_stock(self, account_id, order_list, confirm=False):
        order_status = {}

        if confirm:
            user_input = input(
                'Would you like to place order? (y/N)? '
            ).upper()

        if confirm and user_input == 'N':
            return order_status


        order_response = self.ib_client.place_orders(
            account_id=account_id,
            orders=order_list
        )

        if order_response:
            response_id_dict = order_response[0]
            reply_id = response_id_dict.get('id', None)
            reply_response = self.ib_client.place_order_reply(
                reply_id=reply_id,
                reply=True)
            order_status = reply_response

        return order_status

    def _update_data_list(self, data_list):
        for item in data_list:
            timestamp_ms = item.pop('t') / 1000
            t_date = datetime.fromtimestamp(int(timestamp_ms), timezone.utc)
            item['Date'] = t_date.date()
            item['Open'] = item.pop('o')
            item['Close'] = item.pop('c')
            item['High'] = item.pop('h')
            item['Low'] = item.pop('l')
            # item['Volume'] = item.pop('v')
            item.pop('v')

        return data_list

    def get_market_data_history(self, contract_id, period, bar):
        # Grab the Market Data History
        try:
            market_data_history_dict = self.ib_client.market_data_history(contract_id, period, bar)
        except HTTPError as e:
            market_data_history_dict = {}

        return market_data_history_dict.get('data', [])

    def get_market_data_history_list(self, contract_id, period, bar):
        data_list = self.get_market_data_history(contract_id, period, bar)
        data_list = self._update_data_list(data_list)

        return data_list

    def get_current_market_data_snapshot(self, conids, attempt=10):
        ''' Get market snapshot current data.'''

        # Below must be called once to receive market data snapshot

        self.ib_client.server_accounts()

        current_time_stamp_ms = int(time.time() * 1000)

        str_conid = '{}'.format(conids)
        conids = [str_conid]
        fields = ['30', '70', '71']

        attempt_data = []
        while attempt:

            attempt_data = self.ib_client.market_data(conids, current_time_stamp_ms, fields)

            if attempt_data and '31' not in attempt_data[0]:
                attempt -= 1
            elif attempt_data and '31' in attempt_data[0]:
                attempt = 0

            time.sleep(0.2)

        return attempt_data

    def get_symbol_by_conid(self, contract_id):
        ''' Return contract id given symbol.'''

        search_result = self.ib_client.contract_details(contract_id)

        return search_result.get('symbol', 'XXX')


    def place_order_with_bollinger_band(self, account_id, conid, side, current_close):
        if side == 'SELL':
            stock_postion_dict = self.search_stock_by_conid(account_id, conid)
            quantity = stock_postion_dict.get('position', 0)

        else:
            # get balance and calculate number of position to buy
            balance_type = 'AVB'
            account_balance_dict = self.get_account_balance(account_id, balance_type)
            account_balance = account_balance_dict.get('amount', 0)
            quantity = account_balance // current_close

        order_dict = {
            'account_id': account_id,
            'conid': conid,
            'side': side,
            'quantity': quantity
        }

        orders = hp.prepare_order_dict_from_args(order_dict)
        order_status = self.place_order_stock(account_id, orders)

        return order_status
