import logging
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
from bob_telegram_tools.bot import TelegramBot
from telegram import *
from telegram.ext import *

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# inisiation type and handling
TIPE, HANDLE_MESSAGE = range(2)

# insert telegram key from botfather
key = "1966602790:AAEMyuwfYfJYUq-QrTeO4ajWTR2GlK1WTVU"
user_id = int()
bot = TelegramBot(key, user_id)
tracker = ''

# start functions


def start(update: Update, context: CallbackContext) -> int:

    # to give the user options on the data
    reply_keyboard = [['Kasus', 'Sembuh', 'Meninggal']]

    # welcome message
    update.message.reply_text(
        'Selamat datang di COVIDBOT - COVID-19 Tracker oleh Rahmawati Fanansyah Putri :) \n\n'
        'Untuk melihat perkembangan kasus COVID-19 di suatu provinsi, silahkan ketik Nama Provinsi yang ingin anda cari',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Silahkan Pilih :'
        ),
    )
    return TIPE

# type function for detecting the data chosen


def tipe(update: Update, context: CallbackContext) -> int:
    # global tracker to save the result
    global tracker
    user = update.message.from_user
    # to check the user log
    logger.info("Tipe data of %s: %s", user.first_name, update.message.text)
    # reading the data chosen by the user
    tracker = str(update.message.text).upper()

    update.message.reply_text(
        'Silahkan ketik Nama Provinsi yang ingin anda cari',
        reply_markup=ReplyKeyboardRemove(),
    )

    return HANDLE_MESSAGE

# function to detect the specific user


def getid(update):
    global bot, key
    user_id = update.message.chat.id
    bot = TelegramBot(key, int(user_id))

# function to handle message by the user


def handle_message(update, context):
    text = str(update.message.text).lower()
    getid(update)
    response = respon(update, text)

    update.message.reply_text(response)

# function to clean the prov format on the JSON


def prov(input):
    provinsi = str(input).upper()
    provinsi = str(provinsi).replace(" ", "_")
    return provinsi

# function to respon the user requested data


def respon(update, input_text):
    user_message = str(input_text).upper()

    provinsi = prov(user_message)
    URL = "https://data.covid19.go.id/public/api/prov_detail_{}.json".format(
        provinsi)

    # checking the JSON if available
    response = requests.get(URL)
    if response:
        print(response)
    else:
        # exception handling
        update.message.reply_text('Pastikan nama Provinsinya benar')

    # data processing
    data = json.loads(response.text)
    df = pd.json_normalize(data['list_perkembangan'])
    # unix date data to human readble
    df.tanggal = pd.to_datetime(df.tanggal, unit='ms')
    lastday = int(df[tracker].tail(1))
    last_data_date = df["tanggal"].iloc[-1]
    last30days = df[tracker].tail(30).mean()

    # matlibplot visualization
    x = df['tanggal']
    y = df[tracker]

    plt.bar(x, y,
            width=0.8)
    plt.plot(x, y, color='black', linewidth=1,
             marker='^', markerfacecolor='red', markersize=3)
    plt.xlabel('Tanggal')
    plt.xticks(rotation=90)
    plt.ylabel('Jumlah {} \n (orang)'.format(tracker))
    plt.title('Grafik {} COVID-19'.format(tracker))

    # plt.show()

    # sending the grapth to the telegram
    bot.send_plot(plt)

    # This method delete the generetad image
    plt.clf()
    bot.clean_tmp_dir()

    # done message
    done_message = 'Diatas merupakan Grafik Jumlah {} COVID-19 di provinsi {} dari awal Corona hingga tanggal {}.\n\nData Terakhir menunjukkan ada {} orang {}.\nRata-rata dalam sebulan terakhir : {:.2f} orang.\n\nuntuk keluar silahkan klik /cancel\n\nuntuk memilih provinsi lagi silahkan ketik nama provinsi : '.format(
        tracker, user_message, last_data_date, lastday, tracker, last30days)

    return done_message

# function to return to the main menu -> re choosing the data type


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Terimakasih sudah menggunakan jasa kami \n untuk kembali ke menu awal silahkan klik /start', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

# main function


def main() -> None:
    updater = Updater(key)

    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            TIPE: [MessageHandler(Filters.regex('^(Kasus|Sembuh|Meninggal)$'), tipe)],
            # LOCATION: [
            #     MessageHandler(Filters.location, location),
            #     CommandHandler('skip', skip_location),
            # ],
            HANDLE_MESSAGE: [MessageHandler(Filters.text & ~Filters.command, handle_message)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
