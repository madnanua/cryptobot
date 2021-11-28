import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# data = pd.read_csv('watchlists on 2021-08-31 16:22:00.csv')
data = pd.read_csv('btc.csv')
data.columns = ['symbol', 'open_date_time', 'open', 'high', 'low',
                'close', 'volume', 'num_trades', 'taker_base_vol', 'taker_quote_vol']

data['change'] = data['close'].astype(float).pct_change()*100
# data['changes'] = data['close'].groupby(
#     ['symbol']).astype(float).pct_change()*100
data['atl'] = data['close'].min()
data['ath'] = data['close'].max()
data['maxvol'] = data['volume'].max()
data['minvol'] = data['volume'].min()

print(data)

x = data['open_date_time']
y = data['close']
v = data['volume']

plt.plot(x, y, linewidth=1)
plt.bar(x, v, width=0.8)

plt.xticks(rotation=90)

data.loc[(data['close'] == data['ath']), [
    'open_date_time', 'close']].plot(marker='v', markersize=3)
data.loc[(data['close'] == data['atl']), [
    'open_date_time', 'close']].plot(marker='^', markersize=3)

# a = data.loc[data['close'] == data['atl'], data['open_date_time']]
# b = data.loc[data['close'] == 50394.85, data['close']]

# print(a)
# print(b)
# plt.plot(a, b, marker='^', markersize=3)

plt.show()
