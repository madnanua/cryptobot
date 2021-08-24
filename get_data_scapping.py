import json
import requests
import pandas as pd
import matplotlib.pyplot as plt
from bob_telegram_tools.bot import TelegramBot


def prov(input):
    provinsi = str(input).upper()
    provinsi = str(provinsi).replace(" ", "_")
    return provinsi


provinsi = prov("Daerah Istimewa Yogyakarta")


URL = "https://data.covid19.go.id/public/api/prov_detail_{}.json".format(
    provinsi)
# df = pd.read_json(URL)
print(URL)

response = requests.get(URL)
data = json.loads(response.text)
df = pd.json_normalize(data['list_perkembangan'])
df.tanggal = pd.to_datetime(df.tanggal, unit='ms')

print(df)

tracker = 'SEMBUH'

x = df['tanggal']
y = df[tracker]

plt.plot(x, y, color='green', linestyle='dashed', linewidth=1,
         marker='^', markerfacecolor='blue', markersize=3)

# plt.bar(x, y,
#         width=0.8)

# naming the x axis
plt.xlabel('Tanggal')
# naming the y axis
plt.ylabel('Jumlah {}'.format(tracker))

# giving a title to my graph
plt.title('Grafik {}'.format(tracker))

# function to show the plot
plt.show()

bot.send_plot(plt)

for i in df:
    print(i)
