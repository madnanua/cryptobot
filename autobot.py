import websocket
import json
import pandas as pd
import logging
from datetime import datetime
logging.basicConfig(filename='autobot.log',
    format='%(asctime)s - %(name)s - %(levelname)s : %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


path = '/home/madnanua/git/csvs/'

stream = "wss://stream.binance.com:9443/ws/!miniTicker@arr"


def on_message(ws, message):
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

ws = websocket.WebSocketApp(stream, on_message=on_message)
ws.run_forever()
