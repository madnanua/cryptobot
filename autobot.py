import websocket
import json
import pandas as pd

path = '/home/madnanua/git/csvs/'

stream = "wss://stream.binance.com:9443/ws/!miniTicker@arr"


def on_message(ws, message):
    msg = json.loads(message)
    symbol = [x for x in msg if x['s'].endswith('USDT')]
    frame = pd.DataFrame(symbol)[['E', 's', 'c']]
    frame.E = pd.to_datetime(frame.E, unit='ms')
    frame.c = frame.c.astype(float)
    for row in range(len(frame)):
        data = frame[row:row+1]
        data[['E', 'c']].to_csv(
            path+data['s'].values[0], mode='a', header=False)


ws = websocket.WebSocketApp(stream, on_message=on_message)
ws.run_forever()
