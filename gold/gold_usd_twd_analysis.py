# gold_usd_twd_analysis.py
# 2025/06/11 - 整合版：圖表輸出、邏輯回歸與隨機森林預測、中文支援

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

# ✅ 中文字體設定
sns.set(style="whitegrid")
if platform.system() == 'Darwin':
    plt.rcParams['font.family'] = ['Arial Unicode MS']
elif platform.system() == 'Windows':
    plt.rcParams['font.family'] = ['Microsoft JhengHei']
else:
    plt.rcParams['font.family'] = ['Noto Sans CJK TC']
plt.rcParams['axes.unicode_minus'] = False

print("✅ Step 1：下載資料")
gold = yf.download("GC=F", start="2018-01-01", end="2024-12-31")
dxy = yf.download("UUP", start="2018-01-01", end="2024-12-31")

if gold.empty or dxy.empty:
    raise Exception("❌ 金價或美元資料下載失敗")

print("✅ Step 2：載入台幣匯率 CSV")
usd_twd = pd.read_csv("./gold/usd_twd.csv", parse_dates=["Date"])
usd_twd.set_index("Date", inplace=True)

print("✅ Step 3：合併所有資料")
df = pd.DataFrame({
    "Gold": gold["Close"].squeeze(),
    "DXY": dxy["Close"].squeeze(),
    "USD_TWD": usd_twd["USD_TWD"].squeeze()
}).dropna()

print("✅ Step 4：計算報酬率")
returns = df.pct_change().dropna()

# Step 5：散佈圖與回歸線
plt.figure(figsize=(8, 6))
sns.regplot(x=returns["DXY"], y=returns["Gold"], line_kws={"color": "red"})
plt.title("黃金報酬 vs 美元 ETF(UUP) 報酬")
plt.xlabel("美元報酬率 (UUP)")
plt.ylabel("黃金報酬率")
plt.tight_layout()
plt.savefig("./gold/scatter_gold_dxy.png")
plt.close()
print("✅ Step 5 散佈圖完成")

# Step 6：相關係數熱力圖
plt.figure(figsize=(6, 5))
sns.heatmap(returns.corr(), annot=True, cmap="coolwarm", fmt=".2f")
plt.title("報酬率相關係數熱力圖")
plt.tight_layout()
plt.savefig("./gold/correlation_heatmap.png")
plt.close()
print("✅ Step 6 熱力圖完成")

# Step 7：漲跌交叉表
bin_returns = returns.copy()
bin_returns["Gold"] = (returns["Gold"] > 0).astype(int)
bin_returns["DXY"] = (returns["DXY"] > 0).astype(int)
crosstab = pd.crosstab(bin_returns["DXY"], bin_returns["Gold"], normalize='index')
crosstab.columns = ["Gold_Down", "Gold_Up"]

print("\n美元上/下漲對黃金漲跌影響：")
print(crosstab)

# Step 7.2：視覺化交叉表
crosstab.plot(kind="bar", stacked=True, colormap="coolwarm")
plt.title("在美元漲/跌下，黃金漲跌機率")
plt.xlabel("美元漲跌 (0=跌, 1=漲)")
plt.ylabel("黃金漲/跌比例")
plt.tight_layout()
plt.savefig("./gold/gold_usd_crosstab.png")
plt.close()
print("✅ Step 7.2 視覺化交叉表完成")

# Step 8：建立預測標籤
returns["Gold_Up_Tomorrow"] = (returns["Gold"].shift(-1) > 0).astype(int)
returns.dropna(inplace=True)

X = returns[["DXY", "USD_TWD"]]
y = returns["Gold_Up_Tomorrow"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Logistic Regression 模型
print("✅ Step 8：Logistic Regression 預測")
log_model = LogisticRegression()
log_model.fit(X_train, y_train)
y_pred_log = log_model.predict(X_test)

print("🎯 Logistic Regression 預測結果")
print("準確率：", accuracy_score(y_test, y_pred_log))
print(classification_report(y_test, y_pred_log))

coef_df = pd.DataFrame({
    "Feature": X.columns,
    "Coefficient": log_model.coef_[0]
})
print("邏輯回歸模型係數：")
print(coef_df)

# Random Forest 模型
print("✅ Step 9：Random Forest 預測")
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)
y_pred_rf = rf_model.predict(X_test)

print("\n🌲 Random Forest 預測結果：")
print("準確率：", accuracy_score(y_test, y_pred_rf))
print(classification_report(y_test, y_pred_rf))

importance_df = pd.DataFrame({
    "Feature": X.columns,
    "Importance": rf_model.feature_importances_
}).sort_values(by="Importance", ascending=False)

print("隨機森林特徵重要性：")
print(importance_df)