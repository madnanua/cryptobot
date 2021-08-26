import logging
import pandas as pd
import matplotlib.pyplot as plt

from telegram import *
from telegram.ext import *
from bob_telegram_tools.bot import TelegramBot

key = "1989173300:AAGYdoiTUsd7bfAPgoJV4gQi-7GX1FFOKko"
user_id = int(1398494211)
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

    sheet_url = 'https://docs.google.com/spreadsheets/d/1UVjkHJAwH6S5LjOSeXSnV6amIrp4TnJL8gsRfqWeNmw/edit#gid=0'
    url_1 = sheet_url.replace("/edit#gid=", "/export?format=csv&gid=")
    df = pd.read_csv(url_1)
    # print(df)
    df = df[1:14]
    print(df)
    result = df[user_message]
    # result = result[-5]

    # create the table
    x = df['BO NAME']
    y = df[user_message]
    plt.bar(x, y,
            width=0.8)
    plt.xticks(rotation=90)

    # send the table
    bot.send_plot(plt)

    # clear Previous Data
    plt.clf()
    bot.clean_tmp_dir()

    result_msg = ("{} Last sales : \n{}".format(user_message, result))

    return result_msg


def handle_message(update, context):
    text = str(update.message.text)
    getid(update)
    response = respon(update, text)

    update.message.reply_text(response)


def start(update: Update, context: CallbackContext) -> int:

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
