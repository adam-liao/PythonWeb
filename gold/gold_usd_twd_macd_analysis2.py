# gold_usd_twd_analysis.py
# 程式目的：分析黃金、美元指數 (UUP) 與台幣匯率 (USD/TWD) 的關係，並使用技術指標 (RSI, MACD)
# 建立 Logistic Regression 和 Random Forest 模型來預測黃金隔日漲跌。
# 作者：adamliao
# 日期：2025/06/11
# 技術指標：含 RSI & MACD
# 模型：Logistic Regression & Random Forest
# 執行環境：Python 虛擬環境 (venv)
# 執行指令範例：
# source venv/bin/activate  # 啟動虛擬環境
# /Users/adamliao/文件/PythonWeb/venv/bin/python /Users/adamliao/文件/PythonWeb/gold/gold_usd_twd_macd_analysis2.py

# 導入所需的函式庫
import yfinance as yf  # 用於下載金融數據
import pandas as pd  # 用於數據處理和分析
import numpy as np  # 用於數值計算
import matplotlib.pyplot as plt  # 用於繪製圖表
import seaborn as sns  # 用於繪製美觀的統計圖表
import os  # 用於操作作業系統功能 (未使用，但保留)
import platform  # 用於偵測作業系統類型，以便設定字體
from sklearn.linear_model import LogisticRegression  # 導入 Logistic Regression 模型
from sklearn.ensemble import RandomForestClassifier  # 導入 Random Forest 分類器
from sklearn.model_selection import train_test_split  # 用於分割訓練集和測試集
from sklearn.metrics import accuracy_score, classification_report  # 用於評估模型性能

# 設定 Seaborn 圖表風格
sns.set(style="whitegrid")

# ✅ 字體設定（支援跨平台中文顯示）
# 偵測作業系統，設定對應的中文支援字體
if platform.system() == 'Darwin': # macOS
    plt.rcParams['font.family'] = ['Arial Unicode MS']
elif platform.system() == 'Windows': # Windows
    plt.rcParams['font.family'] = ['Microsoft JhengHei']
else: # 其他系統，例如 Linux
    plt.rcParams['font.family'] = ['Noto Sans CJK TC']

# 解決 Matplotlib 中負號顯示問題
plt.rcParams['axes.unicode_minus'] = False

# ✅ Step 1: 下載資料
print("✅ Step 1: 資料下載")
# 從 yfinance 下載黃金期貨 (GC=F) 的歷史數據
gold = yf.download("GC=F", start="2018-01-01", end="2024-12-31")
# 從 yfinance 下載美元指數 ETF (UUP) 的歷史數據
dxy = yf.download("UUP", start="2018-01-01", end="2024-12-31")
# 從本地 CSV 檔案讀取 USD/TWD 匯率數據
usd_twd = pd.read_csv("./gold/usd_twd.csv", parse_dates=["Date"])
# 將 Date 欄位設定為索引
usd_twd.set_index("Date", inplace=True)

# 檢查資料是否成功下載，如果任一數據為空則拋出異常
if gold.empty or dxy.empty:
    raise Exception("❌ 金價或美元 ETF（UUP）資料下載失敗")

# ✅ Step 2: 合併資料
print("✅ Step 2: 整合數據")
# 創建一個新的 DataFrame，包含黃金、DXY 和 USD_TWD 的收盤價
# .squeeze() 用於確保選取的列是 Series 而不是 DataFrame
df = pd.DataFrame({
    "Gold": gold["Close"].squeeze(),
    "DXY": dxy["Close"].squeeze(),
    "USD_TWD": usd_twd["USD_TWD"].squeeze()
# 刪除任何包含 NaN 值的列 (通常是日期不對齊造成的)
}).dropna()

# ✅ Step 3: 計算報酬率
# 計算每日的百分比變化 (報酬率)
returns = df.pct_change().dropna() # 再次刪除因 pct_change 產生的 NaN (第一行)

# ✅ Step 4: 加入技術指標 RSI (相對強弱指數)
print("✅ Step 4: RSI 指標計算")
# 計算黃金價格的每日變化
delta = df["Gold"].diff()
# 計算上漲日的平均漲幅 (14天移動平均)
gain = (delta.where(delta > 0, 0)).rolling(14).mean()
# 計算下跌日的平均跌幅 (取絕對值，14天移動平均)
loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
# 計算相對強弱 (RS)
rs = gain / loss
# 計算 RSI 指數，並加入到 DataFrame 中
df["RSI"] = 100 - (100 / (1 + rs))

# ✅ Step 5: 加入技術指標 MACD (移動平均收斂發散指標)
print("✅ Step 5: MACD 指標計算")
# 計算黃金價格的 12 天指數移動平均 (EMA)
ema12 = df["Gold"].ewm(span=12, adjust=False).mean()
# 計算黃金價格的 26 天指數移動平均 (EMA)
ema26 = df["Gold"].ewm(span=26, adjust=False).mean()
# 計算 MACD 線 (12天 EMA - 26天 EMA)
df["MACD"] = ema12 - ema26
# 計算 MACD 信號線 (MACD 線的 9 天 EMA)
df["MACD_signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

# ✅ Step 6: 散佈圖
print("✅ Step 6: 繪製散佈圖")
# 創建一個新的圖表
plt.figure(figsize=(8,6))
# 繪製美元 ETF 報酬率 vs 黃金報酬率的散佈圖，並加入回歸線
sns.regplot(x=returns["DXY"], y=returns["Gold"], line_kws={"color":"red"})
# 設定圖表標題和軸標籤
plt.title("黃金報酬 vs 美元 ETF 報酬")
plt.xlabel("美元報酬率")
plt.ylabel("黃金報酬率")
# 自動調整圖表佈局，防止標籤重疊
plt.tight_layout()
# 將圖表儲存為 PNG 檔案
plt.savefig("./gold/scatter_gold_dxy.png")
# 關閉圖表，釋放記憶體
plt.close()
print("✅ Step 6.2 散佈圖完成")

# ✅ Step 7: 熱力圖
print("✅ Step 7: 繪製熱力圖")
# 計算報酬率 DataFrame 的相關係數矩陣
corr_matrix = returns.corr()
# 創建一個新的圖表
plt.figure(figsize=(6,5))
# 繪製相關係數熱力圖，顯示數值並使用 coolwarm 色彩映射
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f")
# 設定圖表標題
plt.title("報酬率相關係數熱力圖")
# 自動調整圖表佈局
plt.tight_layout()
# 將圖表儲存為 PNG 檔案
plt.savefig("./gold/correlation_heatmap.png")
# 關閉圖表
plt.close()
print("✅ Step 7.2 熱力圖完成")

# ✅ Step 8: 漲跌交叉表分析
print("✅ Step 8: 漲跌交叉表分析")
# 複製報酬率 DataFrame
bin_returns = returns.copy()
# 將黃金報酬率轉換為二元值：>0 為 1 (漲)，<=0 為 0 (跌)
bin_returns["Gold"] = (returns["Gold"] > 0).astype(int)
# 將美元 ETF 報酬率轉換為二元值：>0 為 1 (漲)，<=0 為 0 (跌)
bin_returns["DXY"] = (returns["DXY"] > 0).astype(int)
# 創建美元漲跌對黃金漲跌的交叉表，並按行進行正規化 (顯示比例)
crosstab = pd.crosstab(bin_returns["DXY"], bin_returns["Gold"], normalize='index')
# 重新命名交叉表的列名以便理解
crosstab.columns = ["Gold_Down", "Gold_Up"]
# 打印交叉表結果
print("\n美元上/下漲對黃金漲跌影響：")
print(crosstab)

# 繪製交叉表的堆疊長條圖
crosstab.plot(kind="bar", stacked=True, colormap="coolwarm")
# 設定圖表標題和軸標籤
plt.title("美元漲跌 vs 黃金漲跌機率")
plt.xlabel("美元漲跌 (0=跌, 1=漲)")
plt.ylabel("黃金漲跌比例")
# 自動調整圖表佈局
plt.tight_layout()
# 將圖表儲存為 PNG 檔案
plt.savefig("./gold/gold_usd_crosstab.png")
# 關閉圖表
plt.close()
print("✅ Step 8.2 視覺化交叉表完成")

# ✅ Step 9: 建立預測模型資料集
print("✅ Step 9: 準備預測模型資料")
# 計算黃金價格的每日報酬率
df["Return"] = df["Gold"].pct_change()
# 創建目標變數：黃金隔日是否上漲 (1=漲, 0=跌)
# .shift(-1) 將報酬率向上移動一行，使其對應到前一天的數據
df["Gold_Up_Tomorrow"] = (df["Return"].shift(-1) > 0).astype(int)

# 刪除包含 NaN 值的行，這些 NaN 值通常來自於技術指標計算的初期以及 shift(-1) 的最後一行
df_model = df.dropna(subset=["RSI", "MACD", "MACD_signal", "Gold_Up_Tomorrow"])

# 定義用於預測的特徵 (自變數)
features = ["DXY", "USD_TWD", "RSI", "MACD", "MACD_signal"]
# 提取特徵數據
X = df_model[features]
# 提取目標變數數據
y = df_model["Gold_Up_Tomorrow"]

# 將數據分割為訓練集和測試集 (80% 訓練，20% 測試)
# random_state 確保每次分割結果一致
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ✅ Step 10: Logistic Regression 模型
print("✅ Step 10: Logistic Regression 預測")
# 初始化 Logistic Regression 模型
# max_iter 增加迭代次數以確保收斂
log_model = LogisticRegression(max_iter=200)
# 使用訓練數據擬合模型
log_model.fit(X_train, y_train)
# 使用測試數據進行預測
y_pred_log = log_model.predict(X_test)

# 打印 Logistic Regression 模型的預測結果評估
print("\n🎯 Logistic Regression 預測結果")
# 打印準確率
print("準確率：", accuracy_score(y_test, y_pred_log))
# 打印詳細的分類報告 (包含精確率、召回率、F1-score 等)
print(classification_report(y_test, y_pred_log))

# 創建一個 DataFrame 來顯示 Logistic Regression 模型的係數
coef_df = pd.DataFrame({
    'Feature': features,
    'Coefficient': log_model.coef_[0] # 提取模型的係數
})
print("\n邏輯回歸模型係數：")
print(coef_df)

# ✅ Step 11: Random Forest 模型
print("✅ Step 11: Random Forest 預測")
# 初始化 Random Forest 分類器
# n_estimators 設定森林中樹的數量
# random_state 確保結果可重現
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
# 使用訓練數據擬合模型
rf_model.fit(X_train, y_train)
# 使用測試數據進行預測
y_pred_rf = rf_model.predict(X_test)

# 打印 Random Forest 模型的預測結果評估
print("\n🌲 Random Forest 預測結果：")
# 打印準確率
print("準確率：", accuracy_score(y_test, y_pred_rf))
# 打印詳細的分類報告
print(classification_report(y_test, y_pred_rf))

# 創建一個 DataFrame 來顯示 Random Forest 模型中各特徵的重要性
feature_importance = pd.DataFrame({
    'Feature': features,
    'Importance': rf_model.feature_importances_ # 提取特徵重要性分數
# 按重要性分數降序排序
}).sort_values(by='Importance', ascending=False)
print("\n隨機森林特徵重要性：")
print(feature_importance)
