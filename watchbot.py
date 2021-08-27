import config
import binance_acc
import logging
import pandas as pd
import matplotlib.pyplot as plt

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


def respon(update, input_text):
    user_message = str(input_text)

    df = binance_acc.df
    result = df
    result_msg = ("Balance are : \n{}".format(result))

    return result_msg


def handle_message(update, context):
    text = str(update.message.text)
    getid(update)
    response = respon(update, text)

    update.message.reply_text(response)


def start(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    # welcome message
    update.message.reply_text(
        'Selamat datang'
    )
    return HANDLE_MESSAGE


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Terimakasih sudah menggunakan jasa kami \n untuk kembali ke menu awal silahkan klik /start', reply_markup=ReplyKeyboardRemove()
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
