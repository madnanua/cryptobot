import pandas as pd
import numpy as np
import ta
import yfinance as yf

symbol = 'ETH-USD'
df = yf.download(symbol, start='2021-08-29', interval='30m')

df['%K'] = ta.momentum.stoch(
    df.High, df.Low, df.Close, window=14, smooth_window=3)
df['%D'] = df['%K'].rolling(3).mean()
df['RSI'] = ta.momentum.rsi(df.Close, window=14)
df['MACD'] = ta.trend.macd_diff(df.Close)

df.dropna(inplace=True)


def gettriggers(df, lags, buy=True):
    dfx = pd.DataFrame()
    for i in range(1, lags+1):
        if buy:
            mask = (df['%K'].shift(i) < 20) & (df['%D'].shift(i) < 20)
        else:
            mask = (df['%K'].shift(i) > 80) & (df['%D'].shift(i) > 80)
        dfx = dfx.append(mask, ignore_index=True)
    return dfx.sum(axis=0)


df['Buytrigger'] = np.where(gettriggers(df, 6,), 1, 0)
df['Selltrigger'] = np.where(gettriggers(df, 6, False), 1, 0)

df['Buy'] = np.where((df.Buytrigger) & (df['%K'].between(20, 80)) & (
    df['%D'].between(20, 80)) & (df['RSI'] > 50) & (df['MACD'] > 0), 1, 0)
df['Sell'] = np.where((df.Selltrigger) & (df['%D'].between(20, 80)) & (
    df['%K'].between(20, 80)) & (df['RSI'] < 50) & (df['MACD'] < 0), 1, 0)

b = [1]
whentobuy = df[df.Buy.isin(b)]
whentosell = df[df.Sell.isin(b)]
buyandsell = [whentobuy, whentosell]
result = pd.concat(buyandsell)
result = result.sort_values(by='Datetime', ascending=True)
print(result)

Buying_dates, Selling_dates = [], []

for i in range(len(df)-1):
    if df.Buy.iloc[i]:
        Buying_dates.append(df.iloc[i+1].name)
        for num, j in enumerate(df.Sell[i:]):
            if j:
                Selling_dates.append(df.iloc[i+num+1].name)
                break

cutit = len(Buying_dates)-len(Selling_dates)

if cutit:
    Buying_dates = Buying_dates[:cutit]

frame = pd.DataFrame({'Buying_dates': Buying_dates,
                     'Selling_dates': Selling_dates})

actuals = frame[frame.Buying_dates > frame.Selling_dates.shift(1)]

print(actuals)


def profitcal():
    buyprice = df.loc[actuals.Buying_dates].Open
    sellprice = df.loc[actuals.Selling_dates].Open
    return (sellprice.values-buyprice.values)/buyprice.values*100


print(symbol, profitcal())

# b = [1]
# whentobuy = df[df.Buy.isin(b)]
# whentosell = df[df.Sell.isin(b)]

# buyandsell = [whentobuy, whentosell]
# result = pd.concat(buyandsell)
# result = result.sort_values(by='Datetime')

# print(result)
# whentobuy, whentosell = [], []

# for i in range(len(df)-1):
#     if df.buy.iloc[i]:
#         whentobuy.append(df.buy.iloc[i+1])
#         for num, j in enumerate(df.sell[i:]):
#             if j:
#                 whentosell.append(df.sell.iloc[i+num+1])
#                 break

# cutit = len(whentobuy) - len(whentosell)

# if cutit:
#     whentobuy = whentobuy[:-cutit]

# frame = pd.DataFrame({'whentobuy': whentobuy, 'whentosell': whentosell})

# print(frame)
