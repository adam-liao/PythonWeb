# 先在終端機輸入 pip install yfinance 安裝套件
# adamliao@ChundeMac-mini lesson8 % source venv/bin/activate
# (venv) adamliao@ChundeMac-mini PythonWeb % python TW2330-0056/TW2330.py

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Step 1: 設定資料期間，下載台積電與0056歷史股價
start_date = "2022-01-01"
end_date = "2024-12-31"

tsmc = yf.download("2330.TW", start=start_date, end=end_date)
etf0056 = yf.download("0056.TW", start=start_date, end=end_date)

# Step 2: 使用調整後收盤價計算每日報酬率（百分比變化）
tsmc['Return'] = tsmc['Close'].pct_change()
etf0056['Return'] = etf0056['Close'].pct_change()

# Step 3: 合併報酬率資料為同一張表
returns = pd.DataFrame({
    'TSMC_Return': tsmc['Return'],
    'ETF0056_Return': etf0056['Return']
}).dropna()

# Step 4: 計算皮爾森相關係數
correlation = returns.corr()
print("台積電與 0056 的報酬率相關係數：")
print(correlation)

# Step 5: 畫出股價趨勢圖
plt.figure(figsize=(14, 6))
plt.plot(tsmc['Close'], label='TSMC (2330.TW)', alpha=0.7)
plt.plot(etf0056['Close']*10, label='0056 ETF (0056.TW)', alpha=0.7)
plt.title('Adjusted Close Price: TSMC vs 0056 ETF')
plt.xlabel('Date')
plt.ylabel('Adjusted Close Price')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()