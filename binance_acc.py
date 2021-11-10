from logging import error
import config
import requests
import pandas as pd
import numpy as np

from tqdm import tqdm
from binance.client import Client
client = Client(config.key_binance, config.secret_binance)

acc_info = client.get_account()

bl = acc_info['balances']
df = pd.DataFrame(bl)
df = df.replace("0.00000000", np.NaN)
df = df[pd.notnull(df['free'])]


def get_watchlists():
    client = Client()
    info = client.get_exchange_info()
    symbols = [x['symbol'] for x in info['symbols']]
    exclude = ['UP', 'DOWN', 'BEAR', 'BULL']
    non_lev = [symbol for symbol in symbols if all(
        excludes not in symbol for excludes in exclude)]
    relevant = [symbol for symbol in non_lev if symbol.endswith('USDT')]
    klines = {}
    for symbol in tqdm(relevant):
        klines[symbol] = client.get_historical_klines(
            symbol, '5m', '1 hour ago UTC')
    returns, symbols, links = [], [], []
    for symbol in relevant:
        if len(klines[symbol]) > 0:
            cumret = ((pd.DataFrame(klines[symbol])[
                4].astype(float).pct_change()+1).prod()-1)*100
            returns.append(cumret)
            symbols.append(symbol)
    retdf = pd.DataFrame(returns, index=symbols, columns=['ret'])
    largest = retdf.ret.nlargest(3).index.tolist()
    smallest = retdf.ret.nsmallest(3).index.tolist()

    for large in largest:
        links.append(
            "https://www.binance.com/en/trade/{}_USDT".format(large[:-4]))
    for small in smallest:
        links.append(
            "https://www.binance.com/en/trade/{}_USDT".format(small[:-4]))
    # print(links)

    message = ("Top 3 Winners & Top 3 Losers : \n{}".format(
        links))
    return message


# print(get_watchlists())


def streams():
    top10_symbols = get_watchlists()
    symbol_trade = top10_symbols[0]
    while True:
        marketprice = 'https://api.binance.com/api/v1/ticker/24hr?symbol=' + symbol_trade
        res = requests.get(marketprice)
        data = res.json()
        lastprice = float(data['lastPrice'])
        return lastprice

# print(top10_symbols)

# while True:
#     print(symbol_trade)
# print(streams())
