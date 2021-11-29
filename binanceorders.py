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

activename = os.path.basename(__file__)
thisfilename = activename.replace(".py","")
dirname = os.path.dirname(__file__)
prevdir = os.path.dirname(dirname)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(levelname)s:%(asctime)s: %(message)s",
                              "%Y-%m-%d %H:%M:%S")
file_handler = logging.FileHandler(f"{thisfilename}-ERROR.log")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.ERROR)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


path = f"{prevdir}/csvs/"
symbols = os.listdir(path)
rets = []
client = Client(binance_key, binance_secret)

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
        data = pd.read_csv(path+symbol, names=['E', 'c'])
        data['E'] = pd.to_datetime(data['E'])
        before = pd.to_datetime('now') - dt.timedelta(minutes=lookback)
        data = data[data.E >= before].reset_index(drop=True)
        data.to_csv(
                path+symbol, header=False)
    except Exception as e:
        logger.exception(f"Data : {e}")
    else:
        return data

def is_consolidating(df, minutes, percentage):
    sec= minutes*60 -1
    recent_candlesticks = df[-sec:]
    
    max_close = recent_candlesticks.c.max()
    min_close = recent_candlesticks.c.min()

    threshold = 1 - (percentage / 100)
    if min_close > (max_close * threshold):
        return True        

    return False

def is_breaking_out(df, minutes,percentage):
    last_close = df[-1:].c.values
    sec = minutes*60-1
    percentage=percentage

    if is_consolidating(df=df[:-1],minutes=minutes, percentage=percentage):
        recent_closes = df[-sec:-1]

        if last_close > recent_closes.c.max():
            cumret = (df.c.pct_change()+1).prod()-1
            return cumret
    return 0

# for symbol in symbols:
#     minutes = 5*60
#     percentage = 2
#     df = last_n_min(symbol, minutes)
#     ret= is_breaking_out(df=df,minutes=minutes,percentage=percentage)
#     rets.append(ret)
    # prices = last_n_min(symbol, 5)
    # cumret = (prices.c.pct_change()+1).prod()-1
    # rets.append(cumret)
# top_coin = symbols[rets.index(max(rets))]
top_coin = 'BTCUSDT'

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
        buynow = datetime.now()
        buystamp = buynow.strftime("%d/%m/%Y %H:%M:%S")
        order = client.order_limit_buy(
            symbol=top_coin, quantity=buy_quantity, price=prize)
        telegram_bot_sendtext(f"{buystamp} : buying {top_coin}")
        buymsg = f"{buystamp} : bought {top_coin} at {order}"
    except Exception as e:
        logger.exception(f"Buying : {e}")
    else:
        print(buymsg)
        buyprice = float(order['price'])
        # buyprice = prize
        ath = buyprice
else:
    print('not going to invest')
    quit()

stream = f"wss://stream.binance.com:9443/ws/{top_coin.lower()}@trade"

def add(retlast):
    try:
        df = pd.read_csv(f"{thisfilename}-RETURN.csv",names=['r'])
    except:
        df = pd.DataFrame({'r':[0]})
        df.to_csv(f"{thisfilename}-RETURN.csv", mode='a', header=False,index=False)
    retprev = df['r'].iloc[-1]
    retnew = float(retlast)+float(retprev)
    df2 = pd.DataFrame({'r': [retnew]})
    df2.to_csv(f"{thisfilename}-RETURN.csv", mode='a', header=False,index=False)

    return retnew

def on_message(ws, message):
    global ath
    try:
        msg = json.loads(message)
    except Exception as e:
        logger.exception(f"Socket : {e}")
    if float(msg['p']) > ath:
        ath = float(msg['p'])
    if float(msg['p']) < ath * 0.985:
        order = client.create_order(
            symbol=top_coin, side='SELL', type='MARKET', quantity=buy_quantity)
        sellnow = datetime.now()
        sellstamp = sellnow.strftime("%d/%m/%Y %H:%M:%S")
        sellmsg = f"{sellstamp} : sold   {top_coin} at {order}"
        try:
            traderes = (float(msg['p'])-float(buyprice))/float(buyprice)*100
            totret=add(retlast=traderes)
            telegrambotmsg= f"{sellstamp} : \n{top_coin} result is {traderes:,.2f}%\nTotal Returns : {totret:,.2f}%"
            telegram_bot_sendtext(telegrambotmsg)
        except Exception as e:
            logger.exception(f"Telegram : {e}")
        else:
            print(sellmsg)
            ws.close()

ws = websocket.WebSocketApp(stream, on_message=on_message)
ws.run_forever()
