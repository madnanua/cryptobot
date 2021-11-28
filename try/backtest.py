import backtrader as bt
import datetime
import pandas as pd


class RSIStrategy(bt.Strategy):

    def __init__(self):
        self.rsi = bt.talib.RSI(self.data, period=14)

    def next(self):
        if self.rsi < 30 and not self.position:
            self.buy(size=1)

        if self.rsi > 70 and self.position:
            self.close()


class buyonlow(bt.Strategy):
    def __init__(self):
        self.bow = 9000
        self.sos = 9400
        self.atl = 10000
        self.ath = 0
        self.buycondition = 10000
        self.atllists = []
        self.x = []

    def next(self):
        if self.atl > self.data.low:
            self.atl = self.data.low
            self.data.buycondition = self.atl * 120 / 100
            print(self.data.buycondition)
            # self.x = self.atllists.append(self.buycondition)
        # if self.data.close > self.atl and not self.position:
        #     self.buy(size=1)

        # if self.data.close < self.data.high:
        #     self.ath = self.data.high
            # self.sellcondition = self.atl * 80 / 100
        # if self.data.close < self.ath and self.position:
        #     self.close()

        # if self.bow > self.data.low and not self.position:
        #     self.buy(size=1)
        # if self.sos < self.data.low and self.position:
        #     self.close()


cerebro = bt.Cerebro()

fromdate = datetime.datetime.strptime('2020-07-01', '%Y-%m-%d')
todate = datetime.datetime.strptime('2020-07-31', '%Y-%m-%d')

data = bt.feeds.GenericCSVData(dataname='btc_15mins.csv', dtformat=2,
                               compression=15, timeframe=bt.TimeFrame.Minutes, fromdate=fromdate, todate=todate)

cerebro.broker.setcommission(commission=0.005)

cerebro.adddata(data)

cerebro.addstrategy(buyonlow)

cerebro.run()

cerebro.plot()
