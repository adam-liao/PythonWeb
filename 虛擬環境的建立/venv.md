## 測試有沒有虛擬環境

which python3

which pip

代表沒有建立虛擬環境 pip not found

## 建立虛擬環境

cd ~/文件/PythonWeb

python3 -m venv venv

# source venv/bin/activate
每次都要先執行 source venv/bin/activate

## 出現虛擬環境

(venv) adamliao@ChundeMac-mini PythonWeb % which python

which pip

列出虛擬環境裡有Python的位置

/Users/adamliao/文件/PythonWeb/venv/bin/python

/Users/adamliao/文件/PythonWeb/venv/bin/pip

## 安裝requests

pip install requests

pip install --upgrade pip

## 回到虛擬環境起動的方式

cd ~/文件/PythonWeb

source venv/bin/activate


✅ 是否每次都要執行 cd 和 source venv/bin/activate？

✔ 是的，每次開啟新終端機或重開機後，都需要重新啟用虛擬環境，才能使用你專案內的 Python 與套件。

原因是：
	•	虛擬環境是「隔離的」，避免影響系統 Python。
 	•	關閉終端機後，虛擬環境就會自動停用，你必須再次 source 來手動啟用。


## 在 VSCode 自動啟用虛擬環境 沒成功

1.	打開 VSCode，按下 Cmd + Shift + P 輸入並選擇：

Python: Select Interpreter

2.	選擇出現的 ./venv/bin/python（通常會自動偵測）。

下次打開這個資料夾時，VSCode 會自動啟用虛擬環境，不需要手動 source！

## 進階

寫入 .bash_profile 或 .zshrc（進階）

如果你每天都只進同一個專案，也可以在 ~/.zshrc 加入：

、、、bash
alias pyweb="cd ~/文件/PythonWeb && source venv/bin/activate"
、、、

以後只要輸入 pyweb 就啟動好了。
