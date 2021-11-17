"""
This script will provide Bollinger Band values for given contract id.
"""
import sys
import os
import argparse
import time
import websocket
import ssl
import random
import _thread
import time
import json
import logging

from ibw.client import IBClient
from ibw.stock import Stock
from utils import helper as hp
from utils.helper import print_df
from utils.settings import BOLLINGER_STREAM_LOG
from utils.settings import ORDER_LOG

MINUTE = 60 # Seconds
NAP_SLEEP = MINUTE
URL = "wss://localhost:5000/v1/api/ws"

def on_message(ws, message):
    global stock_obj
    global market_data_dict, conids, symbols, add_data_once
    global period, lower, upper
    global NAP_SLEEP

    message_dict = json.loads(message.decode('utf-8'))
    conid = str(message_dict.get('conid',''))
    symbol = symbols.get(conid)
    market_data_list = market_data_dict.get(conid)
    current_close = message_dict.get('31', 0)
    current_close = hp.convert_str_into_number(current_close)

    with open(BOLLINGER_STREAM_LOG.as_posix(), 'a') as f:

        print('{current_time} {contract_id}[{symbol}] Current market data snapshot {snapshot_data}.'.format(
            current_time=hp.get_datetime_obj_in_str(),
            snapshot_data=message_dict,
            contract_id=conid,
            symbol=symbol
            ),
            file=f
        )

    if current_close > 0:

        snapshot_data_dict = hp.update_current_market_data(message_dict)

        if add_data_once[conid]:
            market_data_list.append(snapshot_data_dict)
            add_data_once[conid] = False
        else:
            market_data_list = market_data_list[:-1]
            market_data_list.append(snapshot_data_dict)

        bolinger_frame = hp.get_bollinger_band(market_data_list, period, upper, lower, plot=False)
        side = hp.get_signal_for_last_frame(bolinger_frame, current_close)

        b_upper = bolinger_frame['Upper'].iloc[-1]
        b_lower = bolinger_frame['Lower'].iloc[-1]

        if side != 'NAN':

            order_status = stock_obj.place_order_with_bollinger_band(account_id, conid, side, current_close)

            with open(BOLLINGER_STREAM_LOG.as_posix(), 'a') as f:
                print("{current_time} {contract_id}[{symbol}] {side} took place against Bollinger Upper {upper} Close {close} Lower {lower}".format(
                    current_time=hp.get_datetime_obj_in_str(),
                    side=side,
                    upper=b_upper,
                    close=current_close,
                    lower=b_lower,
                    contract_id=conid,
                    symbol=symbol
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
                    contract_id=conid,
                    symbol=symbol
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
                    contract_id=conid,
                    symbol=symbol
                    ),
                    file=f
                )

def on_error(ws, error):
    global conid
    ws.send("umd+{}+{{}}".format(conid))

def on_close(ws, close_status_code, close_msg):
    global conid
    ws.send("umd+{}+{{}}".format(conid))
    print("{} exited with code {} and message {}.".format(ws, close_status_code, close_msg))

def on_open(ws):
    def run(*args):

        global conids
        global market_data_dict
        global symbols

        while True:
            for conid in conids:
                if market_data_dict.get(conid, []):

                    current_price_cmd = 'smd+{}+{{"fields":["31","70","71"]}}'.format(int(conid))
                    for i in range(3):
                        ws.send(current_price_cmd)
                        time.sleep(1)
                else:
                    with open(BOLLINGER_STREAM_LOG.as_posix(), 'a') as f:
                        print('{current_time} {contract_id}[{symbol}] Market Data is empty for the conid.'.format(
                            current_time=hp.get_datetime_obj_in_str(),
                            contract_id=conid,
                            symbol=symbols.get(conid,'')
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

        # ws.close()
    _thread.start_new_thread(run, ())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Buy or Sell stock with Interactive Brokers.')
    parser.add_argument('--username', required=True, help='YOUR_USERNAME')
    parser.add_argument('--account-id', required=True, help='YOUR_ACCOUNT_NUMBER')
    parser.add_argument('--conids', help='STOCK_CONTRACT_ID1,STOCK_CONTRACT_ID2')
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
    
    account_id = args.account_id
    period = args.period
    upper = args.upper
    lower = args.lower
    time_period = args.time_period
    bar = args.bar

    stock_obj = Stock(ib_client)
    stock_obj.ib_client.server_accounts()

    if args.conids:
        conids = args.conids.split(',')
    else:
        conids = stock_obj.get_all_conids_by_account_id(account_id)
        conids = list(map(str ,conids))

    market_data_dict = {}
    symbols = {}
    add_data_once = {}

    for conid in conids:
        symbol = stock_obj.get_symbol_by_conid(conid)
        symbols[conid] = symbol
        add_data_once[conid] = True

        attempt = 3
        while attempt > 0:
            market_data_list = stock_obj.get_market_data_history_list(conid, time_period, bar)
            if market_data_list:
                market_data_dict[conid] = market_data_list
                attempt = 0
            attempt -= 1
            time.sleep(1)
    else:
        stock_obj.ib_client.unsubscribe_all_market_data_history()

    if any(market_data_list != [] for market_data_list in market_data_dict.values()):

        websocket.enableTrace(True)
        ws = websocket.WebSocketApp(URL,
                                  on_open=on_open,
                                  on_message=on_message,
                                  on_error=on_error,
                                  on_close=on_close)

        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    else:
        with open(BOLLINGER_STREAM_LOG.as_posix(), 'a') as f:
            print('{current_time} Market data history is empty {market_data_dict}'.format(
                current_time=hp.get_datetime_obj_in_str(),
                market_data_dict=market_data_dict
                ),
                file=f
            )

