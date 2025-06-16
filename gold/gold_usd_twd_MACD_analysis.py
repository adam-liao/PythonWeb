# gold/gold_rsi_macd_plot.py
# 2025/06/11 - 自動產生 RSI & MACD 線圖並存檔

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import os

# 建立儲存資料夾
output_dir = "./gold"
os.makedirs(output_dir, exist_ok=True)

# 下載黃金期貨資料
gold = yf.download("GC=F", start="2018-01-01", end="2024-12-31")
gold["Close"] = gold["Close"].squeeze()

# 計算 RSI
delta = gold["Close"].diff()
gain = delta.where(delta > 0, 0).rolling(14).mean()
loss = -delta.where(delta < 0, 0).rolling(14).mean()
rs = gain / loss
gold["RSI"] = 100 - (100 / (1 + rs))

# 計算 MACD
ema12 = gold["Close"].ewm(span=12, adjust=False).mean()
ema26 = gold["Close"].ewm(span=26, adjust=False).mean()
gold["MACD"] = ema12 - ema26
gold["MACD_signal"] = gold["MACD"].ewm(span=9, adjust=False).mean()

# 繪製 RSI 圖
plt.figure(figsize=(10, 4))
gold["RSI"].plot(title="RSI (14-day)", color="purple")
plt.axhline(70, color='red', linestyle='--', linewidth=1)
plt.axhline(30, color='green', linestyle='--', linewidth=1)
plt.tight_layout()
plt.savefig(f"{output_dir}/gold_rsi.png")
plt.close()

# 繪製 MACD 圖
plt.figure(figsize=(10, 4))
gold["MACD"].plot(label="MACD", color="blue")
gold["MACD_signal"].plot(label="Signal", color="orange")
plt.title("MACD vs Signal Line")
plt.legend()
plt.tight_layout()
plt.savefig(f"{output_dir}/gold_macd.png")
plt.close()

print("✅ RSI 與 MACD 圖表已儲存完成")
