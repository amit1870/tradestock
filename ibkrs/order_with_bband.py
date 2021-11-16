"""
This script will provide Bollinger Band values for given contract id.
"""
import sys
import os
import argparse
import time

from ibw.client import IBClient
from ibw.stock import Stock
from utils import helper as hp
from utils.helper import print_df
from utils.settings import BOLLINGER_STREAM_LOG, ORDER_LOG

MINUTE = 60 # Seconds
NAP_SLEEP = MINUTE

def run_bollinger_on_conid(stock_obj, market_data_list, conid, current_close, period, upper, lower, symbol, plot=False):
    bolinger_frame = hp.get_bollinger_band(market_data_list, period, upper, lower, plot=plot, symbol=symbol)
    side = hp.get_signal_for_last_frame(bolinger_frame, current_close)

    b_upper = bolinger_frame['Upper'].iloc[-1]
    b_lower = bolinger_frame['Lower'].iloc[-1]

    return side, b_upper, b_lower

def main(ib_client, args):

    stock_obj = Stock(ib_client)
    stock_obj.ib_client.server_accounts()

    conids = args.conids.split(',')
    account_id = args.account_id
    market_data_dict = {}
    symbols = {}
    add_data_once = {}

    for conid in conids:
        symbol = stock_obj.get_symbol_by_conid(conid)
        symbols[conid] = symbol
        add_data_once[conid] = True
        market_data_dict[conid] = stock_obj.get_market_data_history_list(conid, args.time_period, args.bar)
    else:
        stock_obj.ib_client.unsubscribe_all_market_data_history()

    if any(market_data_list != [] for market_data_list in market_data_dict.values()):

        current_market_data = stock_obj.get_current_market_data_snapshot(args.conids)

        while current_market_data:

            with open(BOLLINGER_STREAM_LOG.as_posix(), 'a') as f:
                print('{current_time} Current market data snapshot {current_market_data}.'.format(
                    current_time=hp.get_datetime_obj_in_str(),
                    current_market_data=current_market_data,
                    ),
                    file=f
                )

            for snapshot_data in current_market_data:

                loop_conid = str(snapshot_data.get('conid', ''))
                loop_symbol = symbols.get(loop_conid)
                market_data_list = market_data_dict.get(loop_conid)

                if market_data_list:

                    with open(BOLLINGER_STREAM_LOG.as_posix(), 'a') as f:
                        print('{current_time} {contract_id}[{symbol}] Current market data snapshot {snapshot_data}.'.format(
                            current_time=hp.get_datetime_obj_in_str(),
                            contract_id=loop_conid,
                            symbol=loop_symbol,
                            snapshot_data=snapshot_data
                            ),
                            file=f
                        )

                    field_31 = snapshot_data.get('31', 0)
                    current_close = hp.convert_str_into_number(field_31)

                    if current_close > 0:
                        snapshot_data_dict = hp.update_current_market_data(snapshot_data)

                        if add_data_once[loop_conid]:
                            market_data_list.append(snapshot_data_dict)
                            add_data_once[loop_conid] = False
                        else:
                            market_data_list = market_data_list[:-1]
                            market_data_list.append(snapshot_data_dict)

                        side, b_upper, b_lower = run_bollinger_on_conid(
                            stock_obj,
                            market_data_list,
                            loop_conid,
                            current_close,
                            period,
                            upper,
                            lower,
                            symbol=loop_symbol,
                            plot=False
                        )

                        if side != 'NAN':
                            order_status = stock_obj.place_order_with_bollinger_band(account_id, loop_conid, side, current_close)

                            with open(BOLLINGER_STREAM_LOG.as_posix(), 'a') as f:
                                print("{current_time} {contract_id}[{symbol}] {side} took place against \
Bollinger Upper {upper} Close {close} Lower {lower}".format(
                                    current_time=hp.get_datetime_obj_in_str(),
                                    side=side,
                                    upper=b_upper,
                                    close=current_close,
                                    lower=b_lower,
                                    contract_id=loop_conid,
                                    symbol=loop_symbol
                                    ),
                                    file=f
                                )

                            with open(ORDER_LOG.as_posix(), 'a') as fo:
                                print("{current_time} {contract_id}[{symbol}] <span style='color:#28a745;'><b>{side}</b></span> took place against \
Bollinger Upper {upper} Close {close} Lower {lower}".format(
                                    current_time=hp.get_datetime_obj_in_str(),
                                    side=side,
                                    upper=b_upper,
                                    close=current_close,
                                    lower=b_lower,
                                    contract_id=loop_conid,
                                    symbol=loop_symbol
                                    ),
                                    file=fo
                                )

                        else:
                            with open(BOLLINGER_STREAM_LOG.as_posix(), 'a') as f:
                                print("{current_time} {contract_id}[{symbol}] Current Close does not cross \
Bollinger Upper {upper} Close {close} Lower {lower}".format(
                                    current_time=hp.get_datetime_obj_in_str(),
                                    upper=b_upper,
                                    close=current_close,
                                    lower=b_lower,
                                    contract_id=loop_conid,
                                    symbol=loop_symbol
                                    ),
                                    file=f
                                )

            tickle_response = stock_obj.ib_client.tickle()
            with open(BOLLINGER_STREAM_LOG.as_posix(), 'a') as f:
                print('{current_time} Tickling server to keep session active with response : {tickle_response}'.format(
                    current_time=hp.get_datetime_obj_in_str(),
                    tickle_response=tickle_response
                    ),
                    file=f
                )
                print('{current_time} Going to take nap for {nap}s....'.format(
                    current_time=hp.get_datetime_obj_in_str(),
                    nap=NAP_SLEEP
                    ),
                    file=f
                )
            time.sleep(NAP_SLEEP)

            current_market_data = stock_obj.get_current_market_data_snapshot(args.conids)

    else:
        with open(BOLLINGER_STREAM_LOG.as_posix(), 'a') as f:
            print('{current_time} Market data history is empty {market_data_dict}'.format(
                current_time=hp.get_datetime_obj_in_str(),
                market_data_dict=market_data_dict
                ),
                file=f
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Buy or Sell stock with Interactive Brokers.')
    parser.add_argument('--username', required=True, help='YOUR_USERNAME')
    parser.add_argument('--account-id', required=True, help='YOUR_ACCOUNT_NUMBER')
    parser.add_argument('--conids', required=True, help='STOCK_CONTRACT_ID1 , STOCK_CONTRACT_ID2')
    parser.add_argument('--passkey', help='YOUR_PASSWORD')
    parser.add_argument('--time-period', default='93d', help='Time period for Market Data')
    parser.add_argument('--period', default=12, type=int, help='Moving Average number')
    parser.add_argument('--bar', default='1d', help='Bar')
    parser.add_argument('--upper', default=2, type=float, help='STD Upper Factor')
    parser.add_argument('--lower', default=2, type=float, help='STD Lower Factor')

    args = parser.parse_args()

    # Create a new session of the IB Web API.
    ib_client = IBClient(
        username=args.username,
        account=args.account_id,
        is_server_running=True
    )
    auth_status = False
    if args.passkey:
        ib_client, auth_status = hp.authenticate_ib_client(ib_client, [args.username], [args.passkey], hard=True)

    main(ib_client, args)
