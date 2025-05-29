import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
import numpy as np
import matplotlib.pyplot as plt
import platform

# plt.rcParams['font.family'] = 'sans-serif'
# plt.rcParams['font.sans-serif'] = [
#     'Microsoft JhengHei',
#     'MingLiU',
#     'Taipei Sans TC Beta',
#     'Noto Sans CJK TC'
# ]
# plt.rcParams['axes.unicode_minus'] = False  # 正常顯示負號

# plt.title('報酬率散佈圖與回歸趨勢線')
# plt.show()


# ✅ 自動判斷作業系統並設定對應字體（支援中文與負號）
if platform.system() == 'Darwin':  # macOS
    plt.rcParams['font.family'] = ['Arial Unicode MS']  # 或 PingFang TC / Heiti TC
elif platform.system() == 'Windows':  # Windows
    plt.rcParams['font.family'] = ['Microsoft JhengHei']  # 微軟正黑體
else:  # Linux / Ubuntu
    plt.rcParams['font.family'] = ['Noto Sans CJK TC']  # 開源中文字體

plt.rcParams['axes.unicode_minus'] = False  # 正常顯示負號（避免顯示成亂碼）




# 報酬率散佈圖 + 回歸線 + 模型斜率】

# 下載資料
start_date = "2022-01-01"
end_date = "2024-12-31"
tsmc = yf.download("2330.TW", start=start_date, end=end_date)
etf0056 = yf.download("0056.TW", start=start_date, end=end_date)

# 計算報酬率
tsmc['Return'] = tsmc['Close'].pct_change()
etf0056['Return'] = etf0056['Close'].pct_change()

# 整合報酬率
returns = pd.DataFrame({
    'TSMC_Return': tsmc['Return'],
    'ETF0056_Return': etf0056['Return']
}).dropna()

# 建立線性回歸模型
X = returns['TSMC_Return'].values.reshape(-1, 1)
y = returns['ETF0056_Return'].values

model = LinearRegression()
model.fit(X, y)

# 取得斜率與截距
slope = model.coef_[0]
intercept = model.intercept_

# 畫圖
plt.figure(figsize=(8, 6))
sns.scatterplot(x=returns['TSMC_Return'], y=returns['ETF0056_Return'], alpha=0.5, label='報酬率點')
plt.plot(returns['TSMC_Return'], model.predict(X), color='red', label=f'趨勢線：y = {slope:.2f}x + {intercept:.4f}')
plt.title('報酬率散佈圖與回歸趨勢線')
plt.xlabel('2330報酬率')
plt.ylabel('0056報酬率')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# 顯示模型參數
print(f"線性回歸模型： y = {slope:.4f} * 台積電報酬率 + {intercept:.4f}")