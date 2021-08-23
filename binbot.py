import pandas as pd
import datetime as dt
from binance.client import Client
import time
import datetime
import numpy
import requests
import os

# variables
ath = 0
atl = 100000
tsh = 0
tsl = 0
position = 0
pnl = 0

while True:

    # API Key (You need to get these from Binance account)
    api_key = 'api_key'
    api_secret = 'api_secret'
    client = Client(api_key=api_key, api_secret=api_secret)

    # ticker of product
    symbo1_trade = 'BNBUSDT'

    # order quantity (more than 10 USDT)
    orderquantity = 35

    # bollingerband length and width
    length = 20
    width = 2

    # market stream data
    marketprice = 'https://api.binance.com/api/v1/ticker/24hr?symbol=' + symbo1_trade
    res = requests.get(marketprice)
    data = res.json()
    lastprice = float(data['lastPrice'])

    # Global Strategy
    def csvkan(symbo1_trade, side, lastprice):
        P = pd.DataFrame(
            {'Time': datetime.datetime.now(), 'symbol': symbo1_trade, 'Side': side, 'Close': lastprice}, index=[0])
        P.to_csv('binbotorders.csv', mode='a', header=False, index=False)

    # Strategy Objects
    def bollingerband(symbol, width, intervalunit, length):

        if intervalunit == '1T':
            start_str = '100 minutes ago UTC'
            interval_data = '1m'

            D = pd.DataFrame(
                client.get_historical_klines(symbol=symbol, start_str=start_str, interval=interval_data))
            D.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades',
                         'taker_base_vol', 'taker_quote_vol', 'is_best_match']
            D['open_date_time'] = [dt.datetime.fromtimestamp(
                x / 1000) for x in D.open_time]
            D['symbol'] = symbol
            D = D[['symbol', 'open_date_time', 'open', 'high', 'low', 'close', 'volume', 'num_trades', 'taker_base_vol',
                   'taker_quote_vol']]

        df = D.set_index("open_date_time")

        df['close'] = df['close'].astype(float)

        df = df['close']

        df1 = df.resample(intervalunit).agg({

            "close": "last"
        })

        unit = width

        band1 = unit * numpy.std(df1['close'][len(df1) - length:len(df1)])

        bb_center = numpy.mean(df1['close'][len(df1) - length:len(df1)])

        band_high = bb_center + band1

        band_low = bb_center - band1

        return band_high, bb_center, band_low

    def reset():
        global position, ath, atl
        position = 0
        ath = 0
        atl = 100000

    # percent in stake
    percent = 0.05 / 100

    if ath < lastprice:
        ath = lastprice
        tsh = ath - ath * percent

    if atl > lastprice:
        atl = lastprice
        tsl = atl - atl * percent
        buycondition =

    if long:
        if lastprice < tsh:
            pnl = lastprice - position
            reset()
            csvkan(symbo1_trade, side="Sell", lastprice)
            long = False
    else:
        if lastprice > buycondition:

    print("{} is closed at {:.2f}" .format(symbo1_trade, lastprice))
    print("{:.2f} {:.2f} {:.2f} {:.2f}".format(ath, tsh, atl, tsl))

    # applying boilinger band strategy
    # bb_1m = bollingerband(symbo1_trade, width, '1T', length)
    # print('1 minute upper center lower: ', bb_1m)

    # if lastprice > bb_1m[0]:
    #     print('sell')
    #     side = "Sell"
    #     print(trailingstops(stops, lastprice))
    #     csvkan(symbo1_trade, side, lastprice)

    # if lastprice < bb_1m[2]:
    #     print('buy')
    #     side = "Buy"
    #     print(trailingstops(stops, lastprice))
    #     csvkan(symbo1_trade, side, lastprice)

    time.sleep(1)

    # try:
    #     if lastprice > bb_1m[0]:
    #         # client.order_market_sell(
    #         #     symbol=symbo1_trade, quantity=orderquantity)
    #         break
    #         # the loop stops if the order is made
    # except:
    #     pass
