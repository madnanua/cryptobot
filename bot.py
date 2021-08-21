import websocket
import json
import pprint
import numpy
# import config
import datetime
import pandas as pd

from binance.client import Client
from binance.enums import *

SOCKET = "wss://stream.binance.com:9443/ws/bnbusdt@kline_1m"

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

TRADE_SYMBOL = 'BNBUSDT'
TRADE_QUANTITY = 0.05

closes = []
in_position = False
position_amount = 0
ath = 0
atl = 100000
balance = 100000
buyat = 0
sellat = 0
sl = 0
pnl = 0
upnl = 0
ts = 0

# client = Client(config.API_KEY, config.API_SECRET)


def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(
            symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True


def csvkan(symbo1_trade, side, lastprice):
    P = pd.DataFrame(
        {'Time': datetime.datetime.now(), 'symbol': symbo1_trade, 'Side': side, 'Close': lastprice}, index=[0])
    P.to_csv('botorders.csv', mode='a', header=False, index=False)


def on_open(ws):
    print('opened connection')


def on_close(ws):
    print('closed connection')


def on_message(ws, message):
    global closes, in_position, balance, atl, ath, buyat, sellat, position_amount, sl, ts, pnl

    # print('received message')
    json_message = json.loads(message)
    # pprint.pprint(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']
    closes.append(float(close))

    if is_candle_closed:
        print(datetime.datetime.now())
        # closes.append(float(close))
        # print(closes[-1])

    if ath < closes[-1]:
        ath = closes[-1]
        ts = 99.95 / 100 * closes[-1]

        # sell condition -- on reversal
        revsell = 0.05 / 100
        sellat = ath - revsell*ath

    if atl > closes[-1]:
        atl = closes[-1]
        sl = 100.05 / 100 * closes[-1]

        # buy condition -- on reversal
        revbuy = 0.05 / 100
        buyat = atl + revbuy*atl

    spread = ath - atl
    atr = spread/closes[-1]*100

    print("Close at {:.2f} ".format(closes[-1]))

    if in_position:
        upnl = (closes[-1] - position_amount) / position_amount * 100
        print("Position ; {:.2f}, floating : {:2f}".format(
            position_amount, upnl))
        if closes[-1] < ts:
            pnl = pnl + closes[-1] - position_amount
            print("selling at {:.2f} with PnL of {:.2f}".format(
                closes[-1], pnl))
            position_amount = 0
            ath = 0
            atl = 100000
            csvkan(symbol_trade=TRADE_SYMBOL,
                   side="Sell", lastprice=closes[-1])
            in_position = False

    else:
        # long condition
        if closes[-1] > buyat:
            position_amount = closes[-1]
            ts = 99.5 / 100 * position_amount
            ath = 0
            atl = 100000
            csvkan(symbol_trade=TRADE_SYMBOL,
                   side="Buy", lastprice=closes[-1])

            print("Bought at {:.2f}".format(closes[-1]))
            in_position = True

        # short condition
        # if closes[-1] < sellat:
        #     position_amount = closes[-1]
        #     sl = 100.05 / 100 * position_amount
        #     atl = 100000
        #     print("Short at {:.2f}".format(closes[-1]))
        #     in_position = True

    # if in_position:
    #     if closes[-1] < sellat:
    #         pnl = closes[-1] - position_amount
    #         print("selling at {:.2f} with PnL of {:.2f}".format(
    #             closes[-1], pnl))
    #         position_amount = 0
    #         in_position = False
    #     else:
    #         print("no position, nothing to do")


# print("Balance : {:.2f}".format(balance))

# if len(closes) > RSI_PERIOD:
# np_closes = numpy.array(closes)
# rsi = talib.RSI(np_closes, RSI_PERIOD)
# print("all rsis calculated so far")
# print(rsi)
# last_rsi = rsi[-1]
# print("Close at {}".format(closes[-1]))
# print("With RSI of {}".format(last_rsi))

# if last_rsi > RSI_OVERBOUGHT:
#     if in_position:
#         print("Overbought! Sell! Sell! Sell!")
# put binance sell logic here
# order_succeeded = order(
#     SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
#         if order_succeeded:
#             in_position = False
#     else:
#         print("It is overbought, but we don't own any. Nothing to do.")

# if last_rsi < RSI_OVERSOLD:
#     if in_position:
#         print("It is oversold, but you already own it, nothing to do.")
#     else:
#         print("Oversold! Buy! Buy! Buy!")
# put binance buy order logic here
# order_succeeded = order(
#     SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
# if order_succeeded:
#     in_position = True


ws = websocket.WebSocketApp(SOCKET, on_open=on_open,
                            on_close=on_close, on_message=on_message)
ws.run_forever()
