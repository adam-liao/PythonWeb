# %%
# ✅ ETF 與台積電報酬率完整批次分析專題版 (整合版)

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
import numpy as np
import platform
import os
from scipy.stats import zscore

# %%
# ✅ 字體設定（支援跨平台中文）
if platform.system() == 'Darwin':
    plt.rcParams['font.family'] = ['Arial Unicode MS']
elif platform.system() == 'Windows':
    plt.rcParams['font.family'] = ['Microsoft JhengHei']
else:
    plt.rcParams['font.family'] = ['Noto Sans CJK TC']

plt.rcParams['axes.unicode_minus'] = False


# %%
# ✅ 資料參數設定
base_stock_symbol = "2330.TW"
base_stock_name = "台積電"

target_list = [
    {"symbol": "0050.TW", "name": "0050元大台灣50ETF"},
    {"symbol": "0056.TW", "name": "0056高股息ETF"},
    {"symbol": "00878.TW", "name": "00878高股息ETF"},
    {"symbol": "00692.TW", "name": "富邦公司治理ETF"}
]
start_date = "2022-01-01"
end_date = "2025-04-30"

# %%
# ✅ 建立儲存資料夾
os.makedirs("ETF分析圖表", exist_ok=True)


# %%
# ✅ 下載台積電資料
base_data = yf.download(base_stock_symbol, start=start_date, end=end_date)
base_data['Return'] = base_data['Close'].pct_change()

# %%
print(base_data)

# %%
# ✅ 整理所有報酬率進行長格式轉換
all_returns = []

all_returns.append(pd.DataFrame({
    '股票名稱': base_stock_name,
    '日報酬率': base_data['Return']
}))

results = []  # 儲存回歸結果

for target in target_list:
    compare_stock_symbol = target["symbol"]
    compare_stock_name = target["name"]

    print(f"\n開始分析 {compare_stock_name}...")

    compare_data = yf.download(compare_stock_symbol, start=start_date, end=end_date)
    compare_data['Return'] = compare_data['Close'].pct_change()

    # 合併報酬率
    returns = pd.DataFrame({
        f'{base_stock_symbol}_Return': base_data['Return'],
        f'{compare_stock_symbol}_Return': compare_data['Return']
    }).dropna()

    # 線性回歸
    X = returns[f'{base_stock_symbol}_Return'].values.reshape(-1, 1)
    y = returns[f'{compare_stock_symbol}_Return'].values

    model = LinearRegression()
    model.fit(X, y)

    slope = model.coef_[0]
    intercept = model.intercept_

    # 計算 Pearson 相關係數
    corr_coef = np.corrcoef(X.flatten(), y)[0, 1]

    results.append({
        "ETF代碼": compare_stock_symbol,
        "ETF名稱": compare_stock_name,
        "斜率": slope,
        "截距": intercept,
        "R值": corr_coef
    })

    # 報酬率加入長格式
    all_returns.append(pd.DataFrame({
        '股票名稱': compare_stock_name,
        '日報酬率': compare_data['Return']
    }))

    # 畫回歸圖
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=returns[f'{base_stock_symbol}_Return'], y=returns[f'{compare_stock_symbol}_Return'], alpha=0.5)
    plt.plot(returns[f'{base_stock_symbol}_Return'], model.predict(X), color='red', label=f'y = {slope:.2f}x + {intercept:.4f}')
    plt.title(f'{base_stock_name} 與 {compare_stock_name} 報酬率回歸')
    plt.xlabel(f'{base_stock_name} 報酬率')
    plt.ylabel(f'{compare_stock_name} 報酬率')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"ETF分析圖表/{compare_stock_symbol}_回歸分析圖.png")
    plt.close()


# %%
# ✅ 匯出回歸總表
result_df = pd.DataFrame(results)
result_df.to_csv("ETF分析圖表/回歸分析總表.csv", index=False)
print("\n所有回歸分析已完成。")
display(result_df)

# %%
returns_long = pd.concat(all_returns).dropna()
plt.figure(figsize=(10, 6))
sns.boxplot(x='股票名稱', y='日報酬率', data=returns_long)
plt.title('台積電與各ETF日報酬率盒鬚圖')
plt.grid(True, axis='y')
plt.tight_layout()
plt.savefig("ETF分析圖表/報酬率盒鬚圖.png")
plt.show()

# %%
# ✅ Z分數標準化盒鬚圖
returns_long['Z分數'] = returns_long.groupby('股票名稱')['日報酬率'].transform(zscore)
plt.figure(figsize=(10, 6))
sns.boxplot(x='股票名稱', y='Z分數', data=returns_long)
plt.title('台積電與各ETF日報酬率 Z分數盒鬚圖')
plt.grid(True, axis='y')
plt.tight_layout()
plt.savefig("ETF分析圖表/報酬率Z分數盒鬚圖.png")
plt.show()

print("\n所有圖表與資料皆已完成儲存。")


