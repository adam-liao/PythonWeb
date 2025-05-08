# 2025/05/08-13:20
import numpy as np
import matplotlib.pyplot as plt

# 頻率範圍：1Hz ~ 20kHz（對數刻度）
f = np.logspace(0, 5, num=2000)  # 1 Hz ~ 100 kHz for better視覺化
w = 2 * np.pi * f
s = 1j * w

# 元件值
R1 = 1800        # 1.8kΩ
C1 = 5e-6        # 5µF
L2 = 0.29e-3     # 0.29mH
C2 = 5e-6        # 5µF
Rload = 8        # 喇叭 8Ω

# 並聯阻抗函數
def parallel(Z1, Z2):
    return 1 / (1/Z1 + 1/Z2)

# 第一段：R1 並聯 C1
Z1 = parallel(R1, 1 / (s * C1))

# 第二段：L2 並聯 C2
Z2 = parallel(s * L2, 1 / (s * C2))

# 總阻抗：Z1 → Z2 → 負載串聯
Z_total = Z1 + Z2 + Rload

# 電壓分壓比：喇叭上的電壓 / 總輸出
H = Rload / Z_total
H_dB = 20 * np.log10(np.abs(H))

# 畫圖
plt.figure(figsize=(10, 6))
plt.semilogx(f, H_dB, label='頻率響應 (dB)')
plt.axvline(1320, color='red', linestyle=':', label='陷波頻率 ≈1320Hz')
plt.title("頻率響應圖：1.8kΩ∥5µF → 0.29mH∥5µF → 8Ω")
plt.xlabel("頻率 (Hz)")
plt.ylabel("增益 (dB)")
plt.grid(True, which='both', ls='--')
plt.legend()
plt.tight_layout()
plt.show()