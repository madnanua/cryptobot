from config import key_binance, secret_binance
from binance.client import Client
import os
import pandas as pd
import datetime as dt
import websocket
import json
import logging
logging.basicConfig(filename='autobot-2.log',
    format='%(asctime)s - %(name)s - %(levelname)s : %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

path = '/home/madnanua/git/csvs/'
client = Client(key_binance, secret_binance)
symbols = os.listdir(path)


def last_n_min(symbol, lookback: int):
    data = pd.read_csv('/home/madnanua/git/csvs/'+symbol, names=['E', 'c'])
    data['E'] = pd.to_datetime(data['E'])
    before = pd.to_datetime('now') - dt.timedelta(minutes=lookback)
    data = data[data.E >= before]
    return data


rets = []

for symbol in symbols:
    prices = last_n_min(symbol, 3)
    cumret = (prices.c.pct_change()+1).prod()-1
    rets.append(cumret)

top_coin = symbols[rets.index(max(rets))]

print(top_coin)

inv_amt = 20
info = client.get_symbol_info(symbol=top_coin)
lotsize = float([i for i in info['filters']
                 if i['filterType'] == 'LOT_SIZE'][0]['minQty'])
prize = float(client.get_symbol_ticker(symbol=top_coin)['price'])
buy_quantity = round(inv_amt/prize/lotsize)*lotsize

if float([i for i in client.get_account()['balances'] if i['asset'] == 'USDT'][0]['free']) > inv_amt:
    buymsg = 'buying {} at {}'.format(top_coin,prize)
    print(buymsg)
    # order = client.order_limit_buy(
    #     symbol=top_coin, quantity=buy_quantity, price=prize)
    logging.info(buymsg)
    buyprice = prize
    # print(prize)
else:
    print('already invested')
    quit()
# buyprice = float(order['price'])

stream = f"wss://stream.binance.com:9443/ws/{top_coin.lower()}@trade"


def on_message(ws, message):
    msg = json.loads(message)
    print(f"{(float(msg['p'])-float(buyprice))/float(buyprice)*100:,.2f}")
    if float(msg['p']) < buyprice * 0.98 or float(msg['p']) > 1.05*buyprice:
        # order = client.create_order(
        #     symbol=top_coin, side='SELL', type='MARKET', quantity=buy_quantity)
        # logging.info(top_coin)
        sellmsg = 'selling {} at {}'.format(top_coin,msg['p'])
        logging.info(sellmsg)
        print(sellmsg)
        ws.close()


ws = websocket.WebSocketApp(stream, on_message=on_message)
ws.run_forever()
