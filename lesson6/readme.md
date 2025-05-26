# 0519


# 資料類型要分辨清楚很重要

每個實體都有自己的屬性及方法

.ipynb 是用來學習研究的 

# 啟動flask

flask --app index run

flask --app index run --debug


# 3頁網頁

from flask import Flask

app = Flask(__name__)

<!-- http://127.0.0.1:5000/ -->
@app.route("/")
def index():
    return "<h1>Hello, World! Flask! </h1><img src='https://fakeimg.pl/300x200/C00CCC' alt=''>"

<!-- http://127.0.0.1:5000/user -->
@app.route("/user")
def user():
    return "<h1>user!</h1><p>這是我的第2頁</p>"

<!-- http://127.0.0.1:5000/product -->
@app.route("/product")
def product():
    return "<h1>product!</h1><p>這是我的第3頁</p>"

