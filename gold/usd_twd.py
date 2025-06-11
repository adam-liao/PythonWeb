import pandas_datareader.data as web
import pandas as pd

# 抓取 FRED 上的美元兌台幣匯率
df = web.DataReader("DEXTWUS", "fred", start="2018-01-01", end="2024-12-31")

# 欄位名稱改為一致
df.rename(columns={"DEXTWUS": "USD_TWD"}, inplace=True)

# 移除空值（FRED 週末與假日沒有報價）
df.dropna(inplace=True)

# 儲存為 csv
df.to_csv("usd_twd.csv")
print("成功儲存 usd_twd.csv！")