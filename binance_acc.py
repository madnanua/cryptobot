from logging import error
import config
import requests
import pandas as pd
import numpy as np

from binance.client import Client
client = Client(config.key_binance, config.secret_binance)

acc_info = client.get_account()

bl = acc_info['balances']
df = pd.DataFrame(bl)
df = df.replace("0.00000000", np.NaN)
df = df[pd.notnull(df['free'])]

symbo1_trade = 'ETHUSDT'


def streams():
    while True:
        marketprice = 'https://api.binance.com/api/v1/ticker/24hr?symbol=' + symbo1_trade
        res = requests.get(marketprice)
        data = res.json()
        lastprice = float(data['lastPrice'])
        return lastprice


stream = streams()
