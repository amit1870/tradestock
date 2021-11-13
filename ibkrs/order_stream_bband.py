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
from utils import settings

MINUTE = 60 # Seconds
NAP_SLEEP = MINUTE / 5
URL = "wss://localhost:5000/v1/api/ws"
first_add_flag = True

def on_message(ws, message):
    global stock_obj
    global market_data_list
    global first_add_flag
    global period, upper, lower

    message_dict = json.loads(message.decode('utf-8'))
    current_close = message.get('31', 0)

    if current_close:

        snapshot_data_dict = hp.update_current_market_data(message_dict)
        if first_add_flag:
            market_data_list.append(snapshot_data_dict)
            first_add_flag = False
        else:
            market_data_list = market_data_list[:-1]
            market_data_list.append(snapshot_data_dict)

        bolinger_frame = hp.get_bollinger_band(market_data_list, period, upper, lower, plot=False)
        side = hp.get_signal_for_last_frame(bolinger_frame, current_close)

        b_upper = bolinger_frame['Upper'].iloc[-1]
        b_lower = bolinger_frame['Lower'].iloc[-1]

        if side != 'NAN':
            order_status = stock_obj.place_order_with_bollinger_band(account_id, conid, side, current_close)

            print("{current_time} {side} took place against with Bollinger Upper {upper} Close {close} Lower {lower}".format(
                current_time=hp.get_datetime_obj_in_str(),
                side=side,
                upper=b_upper,
                close=current_close,
                lower=b_lower
                )
            )
        else:
            print("{current_time} Current Close does not cross Bollinger Upper {upper} Close {close} Lower {lower}".format(
                current_time=hp.get_datetime_obj_in_str(),
                upper=b_upper,
                close=current_close,
                lower=b_lower
                )
            )

            tickle_response = stock_obj.ib_client.tickle()
            print('{current_time} Tickling server to keep session active with response : {tickle_response}'.format(
                current_time=hp.get_datetime_obj_in_str(),
                tickle_response=tickle_response
                )
            )



def on_error(ws, error):
    global conid
    ws.send("umd+{}".format(conid))

def on_close(ws, close_status_code, close_msg):
    global conid
    ws.send("umd+{}".format(conid))
    print("{} exited with code {} and message {}.".format(ws, close_status_code, close_msg))

def on_open(ws):
    def run(*args):
        current_price_cmd = 'smd+{}+{{"fields":["31","70","71"]}}'.format(conid)

        while True:
            ws.send(current_price_cmd)
            print('{current_time} Going to take nap for {nap}s....'.format(
                current_time=hp.get_datetime_obj_in_str(),
                nap=NAP_SLEEP
                )
            )
            time.sleep(NAP_SLEEP)

        # ws.close()
    _thread.start_new_thread(run, ())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Buy or Sell stock with Interactive Brokers.')
    parser.add_argument('--username', required=True, help='YOUR_USERNAME')
    parser.add_argument('--account-id', required=True, help='YOUR_ACCOUNT_NUMBER')
    parser.add_argument('--conid', required=True, type=int, help='STOCK_CONTRACT_ID')
    parser.add_argument('--passkey', help='YOUR_PASSWORD')
    parser.add_argument('--time-period', default='93d', help='Time period for Market Data')
    parser.add_argument('--period', default=12, type=int, help='Moving Average number')
    parser.add_argument('--bar', default='1d', help='Bar')
    parser.add_argument('--upper', default=2, type=float, help='STD Upper Factor')
    parser.add_argument('--lower', default=2, type=float, help='STD Lower Factor')

    args = parser.parse_args()

    conid = args.conid
    account_id = args.account_id
    period = args.period
    upper = args.upper
    lower = args.lower

    # Create a new session of the IB Web API.
    ib_client = IBClient(
        username=args.username,
        account=args.account_id,
        is_server_running=True
    )
    auth_status = False
    if args.passkey:
        ib_client, auth_status = hp.authenticate_ib_client(ib_client, [args.username], [args.passkey], hard=True)

    
    stock_obj = Stock(ib_client)
    market_data_list = stock_obj.get_market_data_history_list(conid, args.time_period, args.bar)

    if market_data_list:

        stock_obj.ib_client.unsubscribe_all_market_data_history()

        websocket.enableTrace(True)
        ws = websocket.WebSocketApp(URL,
                                  on_open=on_open,
                                  on_message=on_message,
                                  on_error=on_error,
                                  on_close=on_close)

        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
