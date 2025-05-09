import numpy as np
import matplotlib.pyplot as plt
import platform

# 設定字型，支援中文顯示
if platform.system() == 'Darwin':  # macOS
    plt.rcParams['font.family'] = ['Arial Unicode MS']
elif platform.system() == 'Windows':  # Windows
    plt.rcParams['font.family'] = ['Microsoft JhengHei']
else:
    plt.rcParams['font.family'] = ['Noto Sans CJK TC']

plt.rcParams['axes.unicode_minus'] = False  # 避免負號顯示錯誤

# 頻率範圍：1Hz ~ 100kHz（對數刻度）
f = np.logspace(0, 5, num=2000)  # 1 Hz ~ 100 kHz
w = 2 * np.pi * f
s = 1j * w

# 元件值
R1 = 1800        # 1.8kΩ
C1 = 5e-6        # 5µF
L2 = 0.29e-3     # 0.29mH
C2 = 5e-6        # 5µF
Rload = 4        # 喇叭 4Ω

# 並聯阻抗函數
def parallel(Z1, Z2):
    return 1 / (1/Z1 + 1/Z2)

# 第一段：R1 並聯 C1
Z1 = parallel(R1, 1 / (s * C1))

# 第一條曲線：第二段 L2 並聯 C2
Z2_1 = parallel(s * L2, 1 / (s * C2))
Z_total_1 = Z1 + Z2_1 + Rload
H_1 = Rload / Z_total_1
H_dB_1 = 20 * np.log10(np.abs(H_1))

# 第二條曲線：第二段只有 L2
Z2_2 = s * L2
Z_total_2 = Z1 + Z2_2 + Rload
H_2 = Rload / Z_total_2
H_dB_2 = 20 * np.log10(np.abs(H_2))

# 標題字串
title_str = f"頻率響應圖：{R1}Ω∥{C1*1e6:.0f}µF → L2段比較 → {Rload}Ω負載"

# 繪圖
plt.figure(figsize=(10, 6))
plt.semilogx(f, H_dB_1, label='L2 並聯 C2', color='blue')
plt.semilogx(f, H_dB_2, label='僅 L2', color='orange')

plt.axvline(1320, color='red', linestyle=':', label='陷波頻率 ≈1320Hz')

plt.title(title_str)
plt.xlabel("頻率 (Hz)")
plt.ylabel("增益 (dB)")
plt.grid(True, which='both', ls='--')
plt.legend()
plt.tight_layout()
plt.show()
