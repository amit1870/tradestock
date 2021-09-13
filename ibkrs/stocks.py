from pprint import pprint
from ibw.client import IBClient
from utils import helper

class Stock(object):
    """Initalizes a new instance of the Stock Object.

        Arguments:
        ----
        session {object} -- Your IB session.

        Usage:
        ----
            >>> stock = Stock(session)
            >>> stock
        """
    def __init__(self, session: object) -> None:
        self.session = session

    def get_stock_list(self, account_id, page_id='0', stock_type='0'):
        """
            Returns a list of stock according to given type.
            By default it will return all stocks.

            NAME: account_id
            DESC: The account ID you wish to return positions for.
            TYPE: String

            NAME: page_id
            DESC: The page you wish to return if there are more than 1. The
                  default value is `0`.
            TYPE: String

            NAME: stock_type
            DESC: The stock type you wish to return . The
                  default value is `0`. Other values are `1` and `-1`.
                  `0` is for all stocks. `1` for Profitable stocks and `-1` for Negative stocks.
            TYPE: String

            ADDITIONAL ARGUMENTS NEED TO BE ADDED!!!!!
        """

        # grab account portfolios
        account_positions = self.session.portfolio_account_positions(
            account_id=account_id,
            page_id=page_id
        )

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

            values = (stock, pnl, currency)

            stock_list.append(values)

            if pnl < 0 :
                negative_stock_list.append(values)
            elif pnl > 0:
                profitable_stock_list.append(values)

        if stock_type == '1':
            return profitable_stock_list
        elif stock_type == '-1':
            return negative_stock_list

        return stock_list

       