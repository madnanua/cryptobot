import config
import pandas as pd
import numpy as np

from binance.client import Client
client = Client(config.key_binance, config.secret_binance)

acc_info = client.get_account()

bl = acc_info['balances']
df = pd.DataFrame(bl)
df = df.replace("0.00000000", np.NaN)
df = df[pd.notnull(df['free'])]
print(df)
