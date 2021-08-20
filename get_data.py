import config

from binance.client import Client
client = Client(config.API_KEY, config.API_SECRET)

acc_info = client.get_account()

balance = acc_info['balances']

print(balance)
