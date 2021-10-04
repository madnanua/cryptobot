import config
import logging
import pandas as pd
import matplotlib.pyplot as plt

from telegram import *
from telegram.ext import *
from bob_telegram_tools.bot import TelegramBot

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

    df = pd.read_csv('branchwise_analysis_report.csv', skiprows=8)
    x = df.index[df['Nomor LR '] == "Halaman Total"]
    df.drop(df.index[[x[0]]], inplace=True)
    df = df[df['Pajak Servis'].notna()]
    resultdf = df[df['Nomor LR '] == user_message]

    if not resultdf.empty:
        result = "Paket Anda diterima pada Tanggal {} \nSilahkan Hubungi Agen Penerima di {}".format(
            resultdf.iloc[0]['Tanggal Pemesanan'], resultdf.iloc[0]['Tujuan'])
    else:
        result = "Pastikan Nomor Tiket (Nomor LR) anda Benar."

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
        'Silahkan masukkan Nomor Tiket (Nomor LR) untuk melihat status Anda'
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
