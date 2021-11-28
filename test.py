import os
import pandas as pd
import datetime as dt
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(levelname)s:%(asctime)s: %(message)s",
                              "%Y-%m-%d %H:%M:%S")
file_handler = logging.FileHandler('/home/madnanua/git/cryptobot/ERROR_autobot-2.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.ERROR)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


path = '/home/madnanua/git/csvs/'
symbols = os.listdir(path)
rets = []

def last_n_min(symbol, lookback: int):
    try:
        data = pd.read_csv('/home/madnanua/git/csvs/'+symbol, names=['E', 'c'])
        data['E'] = pd.to_datetime(data['E'])
        before = pd.to_datetime('now') - dt.timedelta(minutes=lookback)
        data = data[data.E >= before]
    except Exception as e:
        logger.exception(f"Data : {e}")
    else:
        return data

def is_consolidating(df, percentage=2):
    recent_candlesticks = df[-200:]
    
    max_close = recent_candlesticks['c'].max()
    min_close = recent_candlesticks['c'].min()

    threshold = 1 - (percentage / 100)
    if min_close > (max_close * threshold):
        return True        

    return False

def is_breaking_out(df, percentage=2.5):
    last_close = df[-1:]['c'].values[0]

    if is_consolidating(df[:-1], percentage=percentage):
        recent_closes = df[-200:-1]

        if last_close > recent_closes['c'].max():
            cumret = (df.c.pct_change()+1).prod()-1
            return cumret
    return 0

# try:
#     for symbol in symbols:
#         prices = last_n_min(symbol, 3)
#         cumret = (prices.c.pct_change()+1).prod()-1
#         rets.append(cumret)
# except Exception as e:
#     logger.exception(f"Returns : {e}")
# else:
#     top_coin = symbols[rets.index(max(rets))]


# symbol = 'BTCUSDT'
for symbol in symbols:
    df = last_n_min(symbol, 5)
    # cumret = (df.c.pct_change()+1).prod()-1
    # print(f"{symbol} : \n{cumret}")
    ret= is_breaking_out(df=df,percentage=2.5)
    print(f"{symbol} : {ret}")
    rets.append(ret)
top_coin = symbols[rets.index(max(rets))]

print(top_coin)