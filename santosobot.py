import config
import logging
import pandas as pd
import matplotlib.pyplot as plt

from telegram import *
from telegram.ext import *
from bob_telegram_tools.bot import TelegramBot
import csv

# paketdatas = ['STSGRG/29', '21-10028STSGRG/Magelang']
included_cols = ['LR Number', 'WayBill No. ']


# read specific columns of csv file using Pandas
df = pd.read_csv("stsdata.csv", usecols=['LR Number', 'WayBill No. '])
print(df)

key = config.key_santoso_bot
user_id = config.user_id
bot = TelegramBot(key, user_id)

HANDLE_MESSAGE = range(1)
# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def getid(update):
    global bot, key
    user_id = update.message.chat.id
    bot = TelegramBot(key, int(user_id))


def respon(update, input_text):
    user_message = str(input_text)
    result = ''

    for i in included_cols:
        if df[i].str.contains(user_message).any():
            result = 'Paket Anda Telah diterima oleh agen pengirim, akan kita informasikan ketika paket sudah sampai di agen tujuan'

    # if user_message in paketdatas:
    #     result = 'Paket Anda Telah diterima oleh agen pengirim, akan kita informasikan ketika paket sudah sampai di agen tujuan'
    if result == '':
        result = 'Pastikan Nomor PNR Anda Benar, untuk membatalkan klik /cancel'

    result_msg = ("Status Paket Anda : \n{}".format(result))
    logger.info("Requested data is sent to %s successfully",
                update.message.from_user.first_name)

    return result_msg


def handle_message(update, context):
    text = str(update.message.text)
    getid(update)
    response = respon(update, text)

    update.message.reply_text(response)


def start(update: Update, context: CallbackContext) -> int:

    # welcome message
    update.message.reply_text(
        'Selamat datang di SANTOSO EXPRESS TRACKER \n\n'
        'Silahkan masukkan PNR (Nomor LR atau Nomor Resi) untuk melihat status pesanana Anda'
    )
    user = update.message.from_user
    logger.info("User %s is asking something.", user.first_name)

    return HANDLE_MESSAGE


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s is done with everything.", user.first_name)
    update.message.reply_text(
        'Terimakasih sudah menggunakan jasa kami \n untuk mengecek paket lain, silahkan klik /start', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    updater = Updater(key)

    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            HANDLE_MESSAGE: [MessageHandler(Filters.text & ~Filters.command, handle_message)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
