import config

from binance.client import Client
client = Client(config.key_binance, config.secret_binance)

acc_info = client.get_account()

balance = acc_info['balances']

print(balance)
