import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 下載資料
start_date = "2022-01-01"
end_date = "2024-12-31"
tsmc = yf.download("2330.TW", start=start_date, end=end_date)
etf0056 = yf.download("0056.TW", start=start_date, end=end_date)

# 計算報酬率
tsmc['Return'] = tsmc['Close'].pct_change()
etf0056['Return'] = etf0056['Close'].pct_change()

# 整理成一張表
returns = pd.DataFrame({
    'TSMC_Return': tsmc['Return'],
    'ETF0056_Return': etf0056['Return']
}).dropna()

# 畫出散佈圖
plt.figure(figsize=(8, 6))
sns.scatterplot(data=returns, x='TSMC_Return', y='ETF0056_Return', alpha=0.5)
plt.title('報酬率散佈圖：2330 vs 0056')
plt.xlabel('2330報酬率')
plt.ylabel('0056報酬率')
plt.grid(True)
plt.tight_layout()
plt.show()