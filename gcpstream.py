import websocket
import json
import pandas as pd
from datetime import datetime
import os
import logging
import requests
from config import telegram_token_error,telegram_chatid

def telegram_bot_senderror(bot_message):
    bot_token = telegram_token_error
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
if not os.path.exists(path):
    os.makedirs(path)
print(path)
stream = "wss://stream.binance.com:9443/ws/!miniTicker@arr"


def on_message(ws, message):
    try:
        msg = json.loads(message)
        symbol = [x for x in msg if x['s'].endswith('USDT')]
        # print(symbol)
        frame = pd.DataFrame(symbol)[['E', 's', 'c']]
        frame.E = pd.to_datetime(frame.E, unit='ms')
        frame.c = frame.c.astype(float)
        for row in range(len(frame)):
            data = frame[row:row+1]
            data[['E', 'c']].to_csv(
                path+data['s'].values[0], mode='a', header=False)
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        logging.info(dt_string)
    except Exception as e:
        logger.exception(f"Socket : {e}")
        telegram_bot_senderror(f"{thisfilename} - Socket : {e}")

ws = websocket.WebSocketApp(stream, on_message=on_message)

def loop1():
    try:
        ws.run_forever()
    except Exception as e:
        telegram_bot_senderror(f"{thisfilename} - Socket : {e}")
    else:
        loop2()

def loop2():
    try:
        ws.run_forever()
    except Exception as e:
        telegram_bot_senderror(f"{thisfilename} - Socket : {e}")
    else:
        loop1()

loop1()