
from bob_telegram_tools.bot import TelegramBot
import matplotlib.pyplot as plt


token = '1966602790:AAEMyuwfYfJYUq-QrTeO4ajWTR2GlK1WTVU'
user_id = int(1398494211)
bot = TelegramBot(token, user_id)

plt.plot([1, 2, 3, 4])
plt.ylabel('some numbers')

bot.send_plot(plt)

# This method delete the generetad image
bot.clean_tmp_dir()
