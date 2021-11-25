import config
import binance_acc
from binance.client import Client
from tqdm import tqdm

import logging
import pandas as pd
import matplotlib.pyplot as plt
import time

from telegram import *
from telegram.ext import *
from bob_telegram_tools.bot import TelegramBot

key = config.key_crpyto_bot
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


def error_handle(update):
    logger.info("There is an error once, retrying..")
    while True:
        try:
            # symbol = get_watchlists().to_string()
            update.message.reply_text(
                binance_acc.get_watchlists()
            )
            logger.info("Please wait for 5 minutes")
            time.sleep(300)
        except:
            update.message.reply_text(
                "ERROR")
            error_handle(update)


def respon(update, input_text):
    user_message = str(input_text).lower()
    result = ''
    try:
        if user_message == "balance":
            df = binance_acc.df
            result = df

        if user_message == "stream":
            df = binance_acc.streams()
            result = df
    except:
        result = "yg lain"

    result_msg = ("{} close at : \n{}".format(
        binance_acc.symbol_trade, result))

    return result_msg


def handle_message(update, context):
    text = str(update.message.text)
    getid(update)
    while True:
        response = respon(update, text)
        update.message.reply_text(response)


def start(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s started the request..", user.first_name)
    while True:
        try:
            # symbol = get_watchlists().to_string()
            update.message.reply_text(
                binance_acc.get_watchlists()
            )
            logger.info("Please wait for 5 minutes")
            time.sleep(300)
            # logger.info("Thanks for Waiting.. Processing the data")
        except:
            update.message.reply_text(
                "ERROR")
            error_handle(update)
            # return HANDLE_MESSAGE


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s cancelled the request.", user.first_name)
    update.message.reply_text(
        'Terimakasih\nuntuk kembali ke menu awal silahkan klik /start', reply_markup=ReplyKeyboardRemove()
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
