from flask import Flask,render_template
# 要載入 這二個套件

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html.jinja2")
# 這裡要指向首頁檔案的名稱

@app.route("/user")
def user():
    return "<h1>user!</h1><p>這是我的第2頁</p>"

@app.route("/product")
def product():
    return "<h1>product!</h1><p>這是我的第3頁</p>"