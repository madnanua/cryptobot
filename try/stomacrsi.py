import pandas as pd
import numpy as np
import ta

df = pd.read_csv('watchlists on 2021-09-18 13:31:00.csv')
df.columns = ['Symbol', 'Open_date_time', 'Open', 'High', 'Low',
              'Close', 'Volume', 'Num_trades', 'Taker_base_vol', 'Taker_quote_vol']

sym = ['BTCUSDT']
df = df[df.Symbol.isin(sym)]

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

Buying_dates, Selling_dates = [], []

# for i in range(len(df)-1):
#     if df.Buy.iloc[i]:
#         Buying_dates.append(df.iloc[i+1].Open_date_time)
#         for num, j in enumerate(df.Sell[i:]):
#             if j:
#                 Selling_dates.append(df.iloc[i+num+1].Open_date_time)
#                 break

# cutit = len(Buying_dates)-len(Selling_dates)

# print(cutit)

# if cutit:
#     Buying_dates = Buying_dates[:cutit]

# frame = pd.DataFrame({'Buying_dates': Buying_dates,
#                      'Selling_dates': Selling_dates})

# actuals = frame[frame.Buying_dates > frame.Selling_dates.shift(1)]

# print(actuals)


# def profitcal():
#     buyprice = df.loc[actuals.Buying_dates].Open
#     sellprice = df.loc[actuals.Selling_dates].Open
#     return (sellprice.values-buyprice.values)/buyprice.values*100


# print(sym, profitcal())

b = [1]
whentobuy = df[df.Buy.isin(b)]
whentosell = df[df.Sell.isin(b)]
buyandsell = [whentobuy, whentosell]
result = pd.concat(buyandsell)
result = result.sort_values(by='Open_date_time', ascending=True)
result.reset_index(level=0, inplace=True)

z = []
for i in range(len(result)):
    if result.Buy.iloc[i-1] & result.Buy.iloc[i]:
        # print(result.Open_date_time.iloc[i])
        z.append(i)
    if result.Sell.iloc[i-1] & result.Sell.iloc[i]:
        # print(result.Open_date_time.iloc[i])
        z.append(i)
        # result.drop([i])
result.drop(z, axis=0, inplace=True)

if result.Sell.loc[0] == 1:
    result.drop(0, axis=0, inplace=True)

if result.Buy.loc[len(result)-1] == 1:
    result.drop(len(result)-1, axis=0, inplace=True)

print(result)
