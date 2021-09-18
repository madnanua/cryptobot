import requests
import pandas as pd
import datetime
# import config
import matplotlib.pyplot as plt


def get_watchlists():
    binanceurl = "https://api.binance.com/api/v3/exchangeInfo"

    req = requests.get(binanceurl)
    req_data = req.json()

    df = pd.json_normalize(req_data['symbols'])
    # filtering USDT pairs
    df = df.loc[df['symbol'].str.contains('USDT')]
    df = df.loc[~df['symbol'].str.contains('UP')]
    df = df.loc[~df['symbol'].str.contains('DOWN')]
    df = df.reset_index()
    wl = df['symbol']
    return wl


symbol = "BTCUSDT"
interval = "30m"
# startTime = int(datetime.datetime(2021, 7, 1).timestamp()*1000)
# endTime = int(datetime.datetime(2021, 8, 1).timestamp()*1000)
startTime = []
endTime = []


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


# eth_data = get_data("BTCUSDT")
# eth_data['change'] = eth_data['close'].astype(float).pct_change()*100

# print(eth_data)

# x = eth_data['open_date_time']
# y = eth_data['volume'].astype(float)
# z = eth_data['close'].astype(float)

# plt.bar(x, y)
# plt.plot(x, z)
# plt.xticks(rotation=90)

# plt.show()

# print watchlists data
now = datetime.datetime.now().replace(second=0, microsecond=0)
csvfilename = ("watchlists on {}.csv".format(now))
print(csvfilename)

watchlists = get_watchlists()
for watchlist in watchlists:
    print(watchlist)
    data = get_data(watchlist)
    data.to_csv(csvfilename, mode='a', header=False, index=False)
