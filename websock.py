import time
import config
import sqlite3
import pandas as pd
import sqlalchemy

from binance import ThreadedWebsocketManager

api_key = config.API_KEY
api_secret = config.API_SECRET

dfs = []

engine = sqlalchemy.create_engine('sqlite:///cry.db')


def main():

    symbol = 'ETHUSDT'

    twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret)
    # start is required to initialise its internal loop
    twm.start()

    def handle_socket_message(msg):
        # print(msg)
        # print(f"Coin : {msg['s']}")
        # print(f"Timestamp : {msg['k']['t']}")
        # print(f"Open : {msg['k']['o']}")
        # print(f"High : {msg['k']['h']}")
        # print(f"Low : {msg['k']['l']}")
        # print(f"Close : {msg['k']['c']}")
        # if float(msg['k']['c']) > 3150.37000000:
        #     print(f"{msg['s']} terbang cuy")

        df = pd.DataFrame(
            {'Symbol': msg['s'], 'Time': msg['E'], 'Close': msg['k']['c'], 'High': msg['k']['h']}, index=[0])
        # df = df.loc[:, ['s', msg['k']['t'], msg['k']['c']]]
        # df.columns = ['Start Time', 'Close Time', 'Symbol',
        #   'Interval', 'First Trade ID', 'Last Trade ID', 'Open', 'Close', 'High', 'Low', 'Base Asset Volume', 'Number of Trades', 'Candle Close', 'Quote asset Volume', 'Taker Buy Base', 'Taker Buy Quote', 'IGNORE']
        # dfs.append(msg['k'])
        df.Time = pd.to_datetime(df.Time, unit='ms')
        df.Close = df.Close.astype(float)
        df.to_sql('ethusdt', engine,
                  if_exists='append', index=False)
        print(df)
        # pd.read_sql('cryptodatabase', engine)
        return (df)

    twm.start_kline_socket(callback=handle_socket_message, symbol=symbol)

# multiple sockets can be started
# twm.start_depth_socket(callback=handle_socket_message, symbol=symbol)

# or a multiplex socket can be started like this
# see Binance docs for stream names
# streams = ['bnbbtc@miniTicker', 'bnbbtc@bookTicker']
# twm.start_multiplex_socket(callback=handle_socket_message, streams=streams)

    twm.join()

    print(df)


if __name__ == "__main__":
    main()
