# gold_usd_twd_分析.py
# 2025/06/11-修正版，使用 UUP 並解決 shape 問題 + 中文字型設定

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import platform



sns.set(style="whitegrid")

# ✅ 字體設定（支援跨平台中文）
if platform.system() == 'Darwin':
    plt.rcParams['font.family'] = ['Arial Unicode MS']
elif platform.system() == 'Windows':
    plt.rcParams['font.family'] = ['Microsoft JhengHei']
else:
    plt.rcParams['font.family'] = ['Noto Sans CJK TC']

plt.rcParams['axes.unicode_minus'] = False

# 1. 下載黃金期貨與美元 ETF 資料
gold = yf.download("GC=F", start="2018-01-01", end="2024-12-31")
dxy = yf.download("UUP", start="2018-01-01", end="2024-12-31")  # 用 UUP 代替 DX-Y.NYB

if gold.empty or dxy.empty:
    raise Exception("❌ 金價或美元指數（UUP）資料下載失敗，請檢查網路或代碼是否正確")

# 2. 載入台幣匯率資料
usd_twd_path = "./gold/usd_twd.csv"
if not os.path.exists(usd_twd_path):
    raise FileNotFoundError(f"❌ 找不到檔案：{usd_twd_path}，請確認檔案位置與名稱")

usd_twd = pd.read_csv(usd_twd_path, parse_dates=["Date"])
usd_twd.set_index("Date", inplace=True)

# 3. 合併資料（使用 squeeze() 確保為一維）
df = pd.DataFrame({
    "Gold": gold["Close"].squeeze(),
    "DXY": dxy["Close"].squeeze(),
    "USD_TWD": usd_twd["USD_TWD"].squeeze()
}).dropna()

# 4. 計算報酬率（百分比變動）
returns = df.pct_change().dropna()

# 5. 散佈圖 + 回歸線
plt.figure(figsize=(8,6))
sns.regplot(x=returns["DXY"], y=returns["Gold"], line_kws={"color":"red"})
plt.title("黃金報酬 vs 美元 ETF(UUP) 報酬")
plt.xlabel("美元報酬率 (UUP)")
plt.ylabel("黃金報酬率")
plt.tight_layout()
plt.savefig("scatter_gold_dxy.png")
plt.show()

# 6. 熱力圖（相關係數）
corr_matrix = returns.corr()
plt.figure(figsize=(6,5))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("報酬率相關係數熱力圖")
plt.tight_layout()
plt.savefig("./gold/correlation_heatmap.png")
plt.show()
# plt.close()
# 7. 漲跌交叉表
print("視覺化交叉表")
bin_returns = returns.copy()
bin_returns["Gold"] = (returns["Gold"] > 0).astype(int)
bin_returns["DXY"] = (returns["DXY"] > 0).astype(int)

crosstab = pd.crosstab(bin_returns["DXY"], bin_returns["Gold"], normalize='index')
crosstab.columns = ["Gold_Down", "Gold_Up"]
print("\n美元上/下漲對黃金漲跌影響：")
print(crosstab)
plt.savefig("gold_usd_crosstab.png")
# plt.close()
print("✅ Step 7.2 視覺化交叉表結束")

print("✅ Step 8 預測模型開始")


# 視覺化交叉表

crosstab.plot(kind="bar", stacked=True, colormap="coolwarm")
plt.title("在美元漲/跌下，黃金漲跌機率")
plt.xlabel("美元漲跌 (0=跌, 1=漲)")
plt.ylabel("黃金漲/跌比例")
plt.tight_layout()
plt.savefig("gold_usd_crosstab.png")
plt.show()
plt.close()

# 8. 邏輯回歸模型預測黃金隔日漲跌
print("✅ 執行第8步：Logistic Regression 開始預測")
returns['Gold_Up_Tomorrow'] = (returns['Gold'].shift(-1) > 0).astype(int)
returns.dropna(inplace=True)  # 移除最後一天（無法判斷明日）

X = returns[['DXY', 'USD_TWD']]
y = returns['Gold_Up_Tomorrow']

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LogisticRegression()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("\n🎯 Logistic Regression 模型預測結果")
print("準確率：", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# 查看模型係數（了解每個特徵影響方向）
coef_df = pd.DataFrame({
    'Feature': X.columns,
    'Coefficient': model.coef_[0]
})
print("\n特徵影響係數：")
print(coef_df)