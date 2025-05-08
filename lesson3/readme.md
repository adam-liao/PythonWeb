### 引數名額 引數值呼叫
模組module裡的方法function
如 random.sample(names,2)

# 下載internet的資源



# 臨時跳過 SSL 驗證
#verify=False 臨時跳過 SSL 驗證（不建議正式環境使用）
response:Response = requests.get(url,verify=False)

# 老師的網址

https://github.com/roberthsu2003/python/tree/master/mini_conda

# minicanda 安裝

conda
# 安裝mini conda

https://docs.anaconda.com/free/miniconda/index.html

新的方法會要從 email 取得下載

# 取消termail一開始就進入base虛擬環境

conda config --set auto_activate_base false

# 世八及pythonconda init

conda init --all bash

# conda版本檢查

conda -V

# 建立虛擬環境

conda create --name myenv python=3.10

# 啟動虛擬環境

conda activate myenv

# 離開虛擬環境

conda deactivate

# 重新安裝套件

# 安裝套件
conda activate myenv
conda install matplotlib
conda install --name myenv matplotlib

# 安裝requirement.txt
 conda install --yes --file requirements.txt

# 檢查目前安裝的套件

conda list

# 刪除虛擬環境

conda env remove --name myenv

# 刪除虛擬環境的套件

conda remove --name myenv matplotlib