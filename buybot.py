import asyncio
from typing import OrderedDict
from binance import AsyncClient, BinanceSocketManager
from numpy import invert
import pandas as pd
import datetime as dt
from binance.client import Client
from config import key_binance, secret_binance


client = Client(key_binance, secret_binance)
