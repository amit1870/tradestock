"""
This module will keep different Trade Algorithm Strategy.
"""

import pandas as pd
import numpy as np

pd.options.mode.chained_assignment = None  # default='warn'

def bolliner_bands(data_list, period, lower_factor=0.5, upper_factor=0.5):
    ''' Bollinger Bands.'''
    df = pd.DataFrame(data_list)

    # set the date as the index
    df = df.set_index(pd.DatetimeIndex(df['Date'].values))

    # Calculate Simple Moving Average, Std Deviation, Upper Band and Lower Band
    df['SMA'] = df['Close'].rolling(window=period).mean()

    df['STD'] = df['Close'].rolling(window=period).std()

    df['Upper'] = df['SMA'] + (df['STD'] * upper_factor)

    df['Lower'] = df['SMA'] - (df['STD'] * lower_factor)

    # create a new data frame
    new_df = df[period-1:]

    return new_df