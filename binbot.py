import pandas as pd
import datetime as dt
from binance.client import Client
# install python-binance
# pip install python-binance
import time
import datetime
import numpy
import requests
import os
# bollingerband using 1 minute data

# Buy if the price is above the upper band

# Sell if the price is below the lower band

# trailing stops
stops = 0


def csvkan(symbo1_trade, side, lastprice):
    P = pd.DataFrame(
        {'Time': datetime.datetime.now(), 'symbol': symbo1_trade, 'Side': side, 'Close': lastprice}, index=[0])
    P.to_csv('binbotorders.csv', mode='a', header=False, index=False)


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

    def trailingstops(stops, lastprice):
        if stops < lastprice:
            stops = lastprice * 95 / 100

        return stops

    bb_1m = bollingerband(symbo1_trade, width, '1T', length)
    # print('1 minute upper center lower: ', bb_1m)

    marketprice = 'https://api.binance.com/api/v1/ticker/24hr?symbol=' + symbo1_trade
    res = requests.get(marketprice)
    data = res.json()
    lastprice = float(data['lastPrice'])

    def alltime(ath=0, atl=100000, lastprice=lastprice):
        if lastprice > ath:
            ath = lastprice
            return ath
        if lastprice < atl:
            atl = lastprice
            return atl

    print("{} is closed at {:.2f}" .format(symbo1_trade, lastprice))

    if lastprice > bb_1m[0]:
        print('sell')
        side = "Sell"
        print(trailingstops(stops, lastprice))
        csvkan(symbo1_trade, side, lastprice)

    if lastprice < bb_1m[2]:
        print('buy')
        side = "Buy"
        print(trailingstops(stops, lastprice))
        csvkan(symbo1_trade, side, lastprice)

    time.sleep(1)

    # try:
    #     if lastprice > bb_1m[0]:
    #         # client.order_market_sell(
    #         #     symbol=symbo1_trade, quantity=orderquantity)
    #         break
    #         # the loop stops if the order is made
    # except:
    #     pass
