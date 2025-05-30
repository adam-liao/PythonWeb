import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
import numpy as np
import platform

# (venv) adamliao@ChundeMac-mini PythonWeb % python TW2330-0056/ML線性回歸3模型.py

# ✅ 自動判斷作業系統並設定對應字體（支援中文與負號）
if platform.system() == 'Darwin':
    plt.rcParams['font.family'] = ['Arial Unicode MS']
elif platform.system() == 'Windows':
    plt.rcParams['font.family'] = ['Microsoft JhengHei']
else:
    plt.rcParams['font.family'] = ['Noto Sans CJK TC']

plt.rcParams['axes.unicode_minus'] = False

# ✅ 可更改參數設定
base_stock_symbol = "2330.TW"
base_stock_name = "台積電"

compare_stock_symbol = "00878.TW"  # 這裡換成你要分析的股票或ETF
compare_stock_name = "00878高股息ETF"  # 自訂義顯示名稱
# compare_stock_symbol = "0056.TW"  # 這裡換成你要分析的股票或ETF
# compare_stock_name = "0056高股息ETF"  # 自訂義顯示名稱

# 下載資料
start_date = "2022-01-01"
end_date = "2024-12-31"

base_data = yf.download(base_stock_symbol, start=start_date, end=end_date)
compare_data = yf.download(compare_stock_symbol, start=start_date, end=end_date)

# 計算報酬率
base_data['Return'] = base_data['Close'].pct_change()
compare_data['Return'] = compare_data['Close'].pct_change()

# 整合報酬率
returns = pd.DataFrame({
    f'{base_stock_name}_Return': base_data['Return'],
    f'{compare_stock_name}_Return': compare_data['Return']
}).dropna()

# 建立線性回歸模型
X = returns[f'{base_stock_name}_Return'].values.reshape(-1, 1)
y = returns[f'{compare_stock_name}_Return'].values

model = LinearRegression()
model.fit(X, y)

# 取得斜率與截距
slope = model.coef_[0]
intercept = model.intercept_

# 畫圖
plt.figure(figsize=(8, 6))
sns.scatterplot(x=returns[f'{base_stock_name}_Return'], y=returns[f'{compare_stock_name}_Return'], alpha=0.5, label='報酬率點')
plt.plot(returns[f'{base_stock_name}_Return'], model.predict(X), color='red',
         label=f'趨勢線：y = {slope:.2f}x + {intercept:.4f}')
plt.title(f'{base_stock_name} 與 {compare_stock_name} 報酬率散佈圖與回歸趨勢線')
plt.xlabel(f'{base_stock_name} 報酬率')
plt.ylabel(f'{compare_stock_name} 報酬率')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# 顯示模型參數
print(f"線性回歸模型： y = {slope:.4f} * {base_stock_name} 報酬率 + {intercept:.4f}")