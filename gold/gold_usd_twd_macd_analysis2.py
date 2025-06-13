# gold_usd_twd_analysis.py
# 2025/06/11 - 含 RSI & MACD 技術指標，Logistic & Random Forest 模型

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import platform
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

sns.set(style="whitegrid")

# ✅ 字體設定（支援跨平台中文）
if platform.system() == 'Darwin':
    plt.rcParams['font.family'] = ['Arial Unicode MS']
elif platform.system() == 'Windows':
    plt.rcParams['font.family'] = ['Microsoft JhengHei']
else:
    plt.rcParams['font.family'] = ['Noto Sans CJK TC']

plt.rcParams['axes.unicode_minus'] = False

# ✅ Step 1: 下載資料
print("✅ Step 1: 資料下載")
gold = yf.download("GC=F", start="2018-01-01", end="2024-12-31")
dxy = yf.download("UUP", start="2018-01-01", end="2024-12-31")
usd_twd = pd.read_csv("./gold/usd_twd.csv", parse_dates=["Date"])
usd_twd.set_index("Date", inplace=True)

if gold.empty or dxy.empty:
    raise Exception("❌ 金價或美元 ETF（UUP）資料下載失敗")

# ✅ Step 2: 合併資料
print("✅ Step 2: 整合數據")
df = pd.DataFrame({
    "Gold": gold["Close"].squeeze(),
    "DXY": dxy["Close"].squeeze(),
    "USD_TWD": usd_twd["USD_TWD"].squeeze()
}).dropna()

# ✅ Step 3: 計算報酬率
returns = df.pct_change().dropna()

# ✅ Step 4: 加入技術指標 RSI
print("✅ Step 4: RSI 指標計算")
delta = df["Gold"].diff()
gain = (delta.where(delta > 0, 0)).rolling(14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
rs = gain / loss
df["RSI"] = 100 - (100 / (1 + rs))

# ✅ Step 5: 加入技術指標 MACD
print("✅ Step 5: MACD 指標計算")
ema12 = df["Gold"].ewm(span=12, adjust=False).mean()
ema26 = df["Gold"].ewm(span=26, adjust=False).mean()
df["MACD"] = ema12 - ema26
df["MACD_signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

# ✅ Step 6: 散佈圖
plt.figure(figsize=(8,6))
sns.regplot(x=returns["DXY"], y=returns["Gold"], line_kws={"color":"red"})
plt.title("黃金報酬 vs 美元 ETF 報酬")
plt.xlabel("美元報酬率")
plt.ylabel("黃金報酬率")
plt.tight_layout()
plt.savefig("./gold/scatter_gold_dxy.png")
plt.close()

# ✅ Step 7: 熱力圖
corr_matrix = returns.corr()
plt.figure(figsize=(6,5))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("報酬率相關係數熱力圖")
plt.tight_layout()
plt.savefig("./gold/correlation_heatmap.png")
plt.close()

# ✅ Step 8: 漲跌交叉表
bin_returns = returns.copy()
bin_returns["Gold"] = (returns["Gold"] > 0).astype(int)
bin_returns["DXY"] = (returns["DXY"] > 0).astype(int)
crosstab = pd.crosstab(bin_returns["DXY"], bin_returns["Gold"], normalize='index')
crosstab.columns = ["Gold_Down", "Gold_Up"]
print("\n美元上/下漲對黃金漲跌影響：")
print(crosstab)

crosstab.plot(kind="bar", stacked=True, colormap="coolwarm")
plt.title("美元漲跌 vs 黃金漲跌機率")
plt.xlabel("美元漲跌 (0=跌, 1=漲)")
plt.ylabel("黃金漲跌比例")
plt.tight_layout()
plt.savefig("./gold/gold_usd_crosstab.png")
plt.close()
print("✅ Step 8.2 視覺化交叉表完成")

# ✅ Step 9: 建立預測模型資料
print("✅ Step 9: 準備預測模型資料")
df["Return"] = df["Gold"].pct_change()
df["Gold_Up_Tomorrow"] = (df["Return"].shift(-1) > 0).astype(int)

df_model = df.dropna(subset=["RSI", "MACD", "MACD_signal", "Gold_Up_Tomorrow"])

features = ["DXY", "USD_TWD", "RSI", "MACD", "MACD_signal"]
X = df_model[features]
y = df_model["Gold_Up_Tomorrow"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ✅ Step 10: Logistic Regression
print("✅ Step 10: Logistic Regression 預測")
log_model = LogisticRegression(max_iter=200)
log_model.fit(X_train, y_train)
y_pred_log = log_model.predict(X_test)

print("\n🎯 Logistic Regression 預測結果")
print("準確率：", accuracy_score(y_test, y_pred_log))
print(classification_report(y_test, y_pred_log))

coef_df = pd.DataFrame({
    'Feature': features,
    'Coefficient': log_model.coef_[0]
})
print("\n邏輯回歸模型係數：")
print(coef_df)

# ✅ Step 11: Random Forest
print("✅ Step 11: Random Forest 預測")
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)
y_pred_rf = rf_model.predict(X_test)

print("\n🌲 Random Forest 預測結果：")
print("準確率：", accuracy_score(y_test, y_pred_rf))
print(classification_report(y_test, y_pred_rf))

feature_importance = pd.DataFrame({
    'Feature': features,
    'Importance': rf_model.feature_importances_
}).sort_values(by='Importance', ascending=False)
print("\n隨機森林特徵重要性：")
print(feature_importance)
