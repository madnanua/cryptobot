from telegram import *
from telegram.ext import *

import logging
import pprint
import requests
import json
from pandas.io.json import json_normalize
import matplotlib.pyplot as plt
import pandas as pd
from bob_telegram_tools.bot import TelegramBot

# insert telegram key from botfather
key = "1966602790:AAEMyuwfYfJYUq-QrTeO4ajWTR2GlK1WTVU"
user_id = int(1398494211)

bot = TelegramBot(key, user_id)

# logger
# logging.basicConfig(level=logging.DEBUG,
#                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logging.getLogger('matplotlib.font_manager').disabled = True

# Telegram functions


def start_command(update, context):
    update.message.reply_text(
        'Selamat datang di COVIDBOT - COVID-19 Tracker oleh Rahmawati Fanansyah Putri :)')
    update.message.reply_text(
        'Untuk melihat perkembangan covid di suatu provinsi, silahkan ketik Nama Provinsi yang ingin anda cari kak ')


def help_command(update, context):
    update.message.reply_text(
        'Silahkan ketik Nama Provinsi yang ingin anda cari')


def handle_message(update, context):
    text = str(update.message.text).lower()
    getid(update)
    response = respon(text)

    update.message.reply_text(response)


def getid(update):
    global bot, key
    user_id = update.message.chat.id
    bot = TelegramBot(key, int(user_id))


def prov(input):
    provinsi = str(input).upper()
    provinsi = str(provinsi).replace(" ", "_")
    return provinsi


def respon(input_text):
    user_message = str(input_text).upper()

    # if user_message in ("CEK"):
    provinsi = prov(user_message)
    try:
        URL = "https://data.covid19.go.id/public/api/prov_detail_{}.json".format(
            provinsi)
    except:
        update.message.reply_text('Pastikan nama Provinsinya benar ya kak :)')

        # df = pd.read_json(URL)
    print(URL)

    response = requests.get(URL)
    if response:
        print(response)
    else:
        update.message.reply_text('Pastikan nama Provinsinya benar')
    data = json.loads(response.text)
    df = pd.json_normalize(data['list_perkembangan'])
    df.tanggal = pd.to_datetime(df.tanggal, unit='ms')

    tracker = 'SEMBUH'

    x = df['tanggal']
    y = df[tracker]

    plt.bar(x, y,
            width=0.8)

    plt.plot(x, y, color='black', linewidth=1,
             marker='^', markerfacecolor='red', markersize=3)

    # naming the x axis
    plt.xlabel('Tanggal')
    # naming the y axis
    plt.ylabel('Jumlah {}'.format(tracker))

    # giving a title to my graph
    plt.title('Grafik {}'.format(tracker))

    # function to show the plot
    # plt.show()

    bot.send_plot(plt)

    # This method delete the generetad image
    plt.clf()
    bot.clean_tmp_dir()

    return user_message


def error(update, context):
    print(f"Error of | {context.error} | Details : {update}")
    # update.message.reply_text(context.error)


def main():
    updater = Updater(key, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("help", help_command))
    # dp.add_handler(MessageHandler(Filters.document.jpg, handle_pictures))
    dp.add_handler(MessageHandler(Filters.text, handle_message))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

# responding chats from the users
