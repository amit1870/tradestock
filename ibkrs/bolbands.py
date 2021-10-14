import argparse
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime, timedelta
from utils.fake_data import DATA

pd.options.mode.chained_assignment = None  # default='warn'
plt.style.use('fivethirtyeight')

def get_signal(data):
    """ Function to get Sell or Buy signal."""
    buy_signal = [] # buy list
    sell_signal = [] # sell list

    for i in range(len(data['Close'])):
        # Sell
        if data['Close'][i] > data['Upper'][i]:
            buy_signal.append(np.nan)
            sell_signal.append(data['Close'][i])
        # Buy
        elif data['Close'][i] < data['Lower'][i]:
            sell_signal.append(np.nan)
            buy_signal.append(data['Close'][i])
        else:
            buy_signal.append(np.nan)
            sell_signal.append(np.nan)

    return buy_signal, sell_signal

def bolliner_bands(data_list, period):
    df = pd.DataFrame(data_list)

    # set the date as the index
    df = df.set_index(pd.DatetimeIndex(df['Date'].values))

    # Calculate Simple Moving Average, Std Deviation, Upper Band and Lower Band
    df['SMA'] = df['Close'].rolling(window=period).mean()

    df['STD'] = df['Close'].rolling(window=period).std()

    df['Upper'] = df['SMA'] + (df['STD'] * 1)

    df['Lower'] = df['SMA'] - (df['STD'] * 1)

    column_list = ['Close', 'SMA', 'Upper', 'Lower']

    df[column_list].plot(figsize=(12.2,6.4))

    plt.title('Bollinger Bands')

    plt.ylabel('USD Price ($)')

    Fig1 = "{}/fig1{}.jpg".format(file_path,period)
    plt.savefig("{}".format(Fig1))

    # plot and shade the area between the two Bollinger bands
    fig = plt.figure(figsize=(12.2,6.4)) # width = 12.2" and height = 6.4"

    # Add the subplot
    ax = fig.add_subplot(1,1,1) # number of rows, cols and index

    # Get the index values of the DataFrame
    x_axis = df.index

    # plot and shade the area between the upper band and the lower band Grey
    ax.fill_between(x_axis, df['Upper'], df['Lower'], color='grey')

    # plot the Closing Price and Moving Average
    ax.plot(x_axis, df['Close'], color='gold', lw=3, label = 'Close Price') #lw = line width

    ax.plot(x_axis, df['SMA'], color='blue', lw=3, label = 'Simple Moving Average')

    # Set the Title & Show the Image
    ax.set_title('Bollinger Bands')
    ax.set_xlabel('Date')
    ax.set_ylabel('USD Price ($)')
    plt.xticks(rotation = 45)
    ax.legend()
    Fig2 = "{}/fig2{}.jpg".format(file_path,period)
    plt.savefig("{}".format(Fig2))

    # create a new data frame
    new_df = df[period-1:]

    # create new columns for the buy and sell signals
    buy_signal, sell_signal = get_signal(new_df)
    new_df['Buy'] = buy_signal
    new_df['Sell'] = sell_signal

    fig = plt.figure(figsize=(12.2,6.4))
    ax = fig.add_subplot(1,1,1)
    x_axis = new_df.index

    # plot and shade the area between the upper band and the lower band Grey
    ax.fill_between(x_axis, new_df['Upper'], new_df['Lower'], color='grey')

    # plot the Closing Price and Moving Average
    ax.plot(x_axis, new_df['Close'], color='gold', lw=3, label = 'Close Price',alpha = 0.5)
    ax.plot(x_axis, new_df['SMA'], color='blue', lw=3, label = 'Moving Average',alpha = 0.5)
    ax.scatter(x_axis, new_df['Buy'] , color='green', lw=3, label = 'Buy',marker = '^', alpha = 1)
    ax.scatter(x_axis, new_df['Sell'] , color='red', lw=3, label = 'Sell',marker = 'v', alpha = 1)

    # set the Title and Show the Image
    ax.set_title('Bollinger Bands')
    ax.set_xlabel('Date')
    ax.set_ylabel('USD Price ($)')
    plt.xticks(rotation = 45)
    ax.legend()
    Fig3 = "{}/fig3{}.jpg".format(file_path,period)
    plt.savefig("{}".format(Fig3))

def update_data(data, start_date_str):
    """ Add Date to each item of list."""
    start_date_j = datetime.strptime(start_date_str, '%Y%m%d-%H:%M:%S')
    start_date = start_date_j.date()
    one_day = timedelta(days=1)
    for item in data:
        item['Date'] = start_date
        item['Open'] = item.pop('o')
        item['Close'] = item.pop('c')
        item['High'] = item.pop('h')
        item['Low'] = item.pop('l')
        
        start_date += one_day

    return data



if __name__ == '__main__':
    DATA_LIST = DATA.get('data', [])
    start_date_str = DATA.get('startTime')
    DATA_LIST = update_data(DATA_LIST, start_date_str)
    period = 3
    bolliner_bands(DATA_LIST, period)