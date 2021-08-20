import websocket
import json
import pprint
import talib
import numpy
import config
import datetime
import pandas as pd

from binance.client import Client
from binance.enums import *

SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

TRADE_SYMBOL = 'ETHUSD'
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

client = Client(config.API_KEY, config.API_SECRET, tld='us')


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


def on_open(ws):
    print('opened connection')


def on_close(ws):
    print('closed connection')


def buy(in_position, position_amount, sellat, buyat, balance):
    if in_position:
        # sell logic
        if sellat > closes[-1]:
            pnl = closes[-1] - position_amount
            # balance update
            balance = balance + position_amount + pnl
            in_position = False

    # buy logic
    if buyat < closes[-1]:
        position_amount = closes[-1]
        balance = balance - position_amount
        in_position = True


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
        # print("Target Sell at : {:.2f}". format(sellat))

    if atl > closes[-1]:
        atl = closes[-1]
        sl = 100.05 / 100 * closes[-1]

        # buy condition -- on reversal
        revbuy = 0.05 / 100
        buyat = atl + revbuy*atl
        # print("Target Buy at : {:.2f}". format(buyat))

    spread = ath - atl
    atr = spread/closes[-1]*100

    # print("Sell  at {:.2f} ".format(sellat))
    print("Close at {:.2f} ".format(closes[-1]))
    # print("Buy   at {:.2f} ".format(buyat))

    # print("ATH : {:.2f} | Spread : {:.2f} / {:.2f}% | ATL : {:.2f}".format(
    #     ath, spread, atr, atl))

    if in_position:
        upnl = (closes[-1] - position_amount) / position_amount * 100
        print("already in position of {:.2f} | stop long at {:.2f}, stop short at {:.2f} | floating at {:.2f}%".format(
            position_amount, ts, sl, upnl))
        if closes[-1] < ts:
            pnl = pnl + closes[-1] - position_amount
            print("selling at {:.2f} with PnL of {:.2f}".format(
                closes[-1], pnl))
            position_amount = 0
            ath = 0
            atl = 100000
            in_position = False
        # if closes[-1] > sl:
        #     pnl = pnl - closes[-1] + position_amount
        #     print("stop shorting at {:.2f} with PnL of {:.2f}".format(
        #         closes[-1], pnl))
        #     position_amount = 0
        #     ath = 0
        #     atl = 100000
        #     in_position = False

    else:
        # long condition
        if closes[-1] > buyat:
            position_amount = closes[-1]
            ts = 99.95 / 100 * position_amount
            ath = 0
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
