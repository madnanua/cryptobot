import pandas as pd

df = pd.read_csv('branchwise_analysis_report (1).csv', skiprows=8)
x = df.index[df['Nomor LR '] == "Halaman Total"]
df.drop(df.index[[x[0]]], inplace=True)
df = df[df['Pajak Servis'].notna()]
resultdf = df[df['Nomor LR '] == "temanggung/4985"]

if not resultdf.empty:
    print("ok")
else:
    print("not ok")

# print("Paket Anda diterima pada Tanggal {} dengan tujuan {}".format(
#     resultdf.iloc[0]['Tanggal Pemesanan'], resultdf.iloc[0]['Tujuan']))
