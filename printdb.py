import sqlalchemy
import pandas as pd

engine = sqlalchemy.create_engine('sqlite:///cry.db')
df = pd.read_sql('ethusdt', engine)

print(df)


df.Close.plot()
