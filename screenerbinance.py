from pandas.core.accessor import register_dataframe_accessor
import config
import pandas as pd
from tqdm import tqdm
from binance.client import Client


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
            symbol, '1m', '1 hour ago UTC')
    returns, symbols, prices = [], [], []
    for symbol in relevant:
        if len(klines[symbol]) > 0:
            cumret = ((pd.DataFrame(klines[symbol])[
                4].astype(float).pct_change()+1).prod()-1)*100
            returns.append(cumret)
            symbols.append(symbol)
    retdf = pd.DataFrame(returns, index=symbols, columns=['ret'])
    message = retdf.ret.idxmax()

    return message


print(get_watchlists())
