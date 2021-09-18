import yfinance as yf
import datetime
import pandas as pd
import requests

symbol = 'BTC-USD'
bsymbol = 'BTCUSDT'
start = '2021-08-28'
startTime = int(datetime.datetime(2021, 8, 28).timestamp()*1000)
# endTime = int(datetime.datetime(2021, 8, 1).timestamp()*1000)
endTime = []
interval = '30m'


def get_data(symbol=symbol, interval=interval, startTime=startTime, endTime=endTime):
    binanceurl = "https://api.binance.com/api/v3/klines"
    params = {'symbol': symbol, 'interval': interval,
              'startTime': startTime, 'endTime': endTime, 'limit': 1000}

    req = requests.get(binanceurl, params=params)
    req_data = req.json()
    df2 = pd.DataFrame(req_data)
    df2.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades',
                   'taker_base_vol', 'taker_quote_vol', 'is_best_match']
    df2['open_date_time'] = [datetime.datetime.fromtimestamp(
        x / 1000) for x in df2.open_time]
    df2['symbol'] = symbol
    df2 = df2[['symbol', 'open_date_time', 'open', 'high', 'low', 'close', 'volume', 'num_trades', 'taker_base_vol',
               'taker_quote_vol']]
    # df2 = df2.set_index("open_date_time")
    return df2


df = yf.download(symbol, start='2021-08-28', interval='30m')

print(df)
print(get_data(bsymbol))
