import pandas as pd
import matplotlib.pyplot as plt


df_raw = pd.read_csv(
    '/Users/kristinemoen/Documents/5-klasse/Master/EEM26/Norge_forbruk_2026-06-04 09_17_37.619667.csv')

#print(df.head())
#print(df.columns)
#print(len(df.columns))


df = df_raw.iloc[:, 0].str.split(',', expand=True)

df.columns = ["START_TIME", "CONSUMPTION_GROUP", "QUANTITY_KWH"]

df["CONSUMPTION_GROUP"] = df["CONSUMPTION_GROUP"].str.replace('"', '')

df["START_TIME"] = pd.to_datetime(df["START_TIME"], format = "mixed")
df["QUANTITY_KWH"] = df["QUANTITY_KWH"].astype(float)

df_pivot = df.pivot(index="START_TIME",
                    columns="CONSUMPTION_GROUP",
                    values="QUANTITY_KWH")


df_pivot.plot(figsize=(12, 6))
#plt.title("Strømforbruk per gruppe (2025)")
plt.xlabel("Month", fontsize = 20)
plt.ylabel("kWh", fontsize = 20)
plt.legend(title="Group")

plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
legend = plt.legend(fontsize=20)
for line in legend.get_lines():
    line.set_linewidth(3)


plt.grid()

plt.show()








