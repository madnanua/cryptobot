from config import binance_key,binance_secret,telegram_token_goog_crpyto,telegram_chatid
from binance.client import Client
import os
import pandas as pd
import datetime as dt
import websocket
import json
import requests
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(levelname)s:%(asctime)s: %(message)s",
                              "%Y-%m-%d %H:%M:%S")
file_handler = logging.FileHandler('ERROR_gcptele.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.ERROR)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


path = '/csvs/'
client = Client(binance_key, binance_secret)
symbols = os.listdir(path)
rets = []

def telegram_bot_sendtext(bot_message):
    bot_token = telegram_token_goog_crpyto
    bot_chatID = telegram_chatid
    try:
        send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    except Exception as e:
        logger.exception(f"Telegram send : {e}")
    try:
        response = requests.get(send_text)
    except Exception as e:
        logger.exception(f"Request : {e}")
    else:
        return response.json()

def last_n_min(symbol, lookback: int):
    try:
        data = pd.read_csv('/csvs/'+symbol, names=['E', 'c'])
        data['E'] = pd.to_datetime(data['E'])
        before = pd.to_datetime('now') - dt.timedelta(minutes=lookback)
        data = data[data.E >= before]
    except Exception as e:
        logger.exception(f"Data : {e}")
    else:
        return data
try:
    for symbol in symbols:
        prices = last_n_min(symbol, 3)
        cumret = (prices.c.pct_change()+1).prod()-1
        rets.append(cumret)
except Exception as e:
    logger.exception(f"Returns : {e}")
else:
    top_coin = symbols[rets.index(min(rets))]

try:
    inv_amt = 20
    info = client.get_symbol_info(symbol=top_coin)
    lotsize = float([i for i in info['filters']
                    if i['filterType'] == 'LOT_SIZE'][0]['minQty'])
    prize = float(client.get_symbol_ticker(symbol=top_coin)['price'])
    buy_quantity = round(inv_amt/prize/lotsize)*lotsize
except Exception as e:
    logger.exception(f"Trade Details : {e}")

if float([i for i in client.get_account()['balances'] if i['asset'] == 'USDT'][0]['free']) > inv_amt:
    try:
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        # order = client.order_limit_buy(
        #     symbol=top_coin, quantity=buy_quantity, price=prize)
        buymsg = f"{dt_string} : bought {top_coin} at {prize}"
    except Exception as e:
        logger.exception(f"Buying : {e}")
    else:
        print(buymsg)
        # buyprice = float(order['price'])
        buyprice = prize
        ath = buyprice
else:
    print('not going to invest')
    quit()

stream = f"wss://stream.binance.com:9443/ws/{top_coin.lower()}@trade"

def add(retlast):
    df = pd.read_csv("returns.csv",names=['r'])
    retprev = df['r'].iloc[-1]
    retnew = float(retlast)+float(retprev)
    df2 = pd.DataFrame({'r': [retnew]})
    df2.to_csv("returns.csv", mode='a', header=False,index=False)

    return retnew

def on_message(ws, message):
    global ath
    msg = json.loads(message)
    if float(msg['p']) > ath:
        ath = float(msg['p'])

    if float(msg['p']) < ath * 0.98:
    # if float(msg['p']) < buyprice * 0.985 or float(msg['p']) > 1.026*buyprice:
            # order = client.create_order(
            #     symbol=top_coin, side='SELL', type='MARKET', quantity=buy_quantity)
        sellmsg = f"{dt_string} : sold   {top_coin} at {msg['p']}"
        try:
            traderes = (float(msg['p'])-float(buyprice))/float(buyprice)*100
            totret=add(retlast=traderes)
            telegrambotmsg= f"{top_coin} result is {traderes:,.2f}%\nTotal Returns : {totret}"
            telegram_bot_sendtext(telegrambotmsg)
        except Exception as e:
            logger.exception(f"Telegram : {e}")
        else:
            print(sellmsg)
            ws.close()

ws = websocket.WebSocketApp(stream, on_message=on_message)
ws.run_forever()
