from logging import error
import config
import requests
import pandas as pd
import numpy as np
import time
from binance import BinanceSocketManager

from binance.client import Client
client = Client(config.key_binance, config.secret_binance)


def get_the_coin():
    all_pairs = pd.DataFrame(client.get_ticker())
    relev = all_pairs[all_pairs.symbol.str.contains('USDT')]
    non_lev = relev[~((relev.symbol.str.contains('UP') |
                      (relev.symbol.str.contains('DOWN'))))]
    top_symbol = non_lev[non_lev.priceChangePercent ==
                         non_lev.priceChangePercent.max()]
    top_symbol = top_symbol.symbol.values[0]
    return top_symbol


def getminutedata(symbol, interval, lookback):
    frame = pd.DataFrame(client.get_historical_klines(
        symbol, interval, lookback+' min ago UTC'))
    frame = frame.iloc[:, :6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame


x = getminutedata(get_the_coin(), '1m', '120')


async def strategy(buy_amt, SL=0.985, Target=1.03, open_position=False):
    try:
        print(f'Trying to get the asset..')
        asset = get_the_coin()
    except:
        time.sleep(61)
        print(f'After sleeping, re-trying to get the asset..')
        asset = get_the_coin()
    socket = bsm.trade_socket(asset)
    df = getminutedata(asset, '1m', '120')
    qty = round(buy_amt/df.Close.iloc[-1])
    if ((df.Close.pct_change()+1).cumprod()).iloc[-1] > 1:
        # order = client.create_order(
        #     symbol=asset, side='BUY', type='MARKET', quantity=qty)
        order = df.Close.iloc[-1]
        print(f'Buy Order : '+str(order))
        # buyprice = float(order['fills'][0]['price'])
        buyprice = order
        open_position = True
        while open_position:
            await socket.__aenter__()
            msg = await socket.recv()
            df = createframe(msg)
            print(f'Close at '+str(df.Price.values))
            print(f'Target at '+str(buyprice*Target))
            print(f'Stop at '+str(buyprice*SL))
            if df.Price.values <= buyprice*SL or df.Price >= buyprice*Target:
                # order = client.create_order(
                #     symbol=asset, side='SELL', quantity=qty)
                print(f'Sell Order : '+str(order))
                break


def createframe(msg):
    df = pd.DataFrame([msg])
    df = df.loc[:, ['s', 'E', 'p']]
    df.columns = ['symbol', 'Time', 'Price']
    df.Price = df.Price.astype(float)
    df.Time = pd.to_datetime(df.Time, unit='ms')
    return df


bsm = BinanceSocketManager(client)
