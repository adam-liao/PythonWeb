from flask import Flask,render_template
# 要載入 這二個套件

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html.jinja2")
# 這裡要指向首頁檔案的名稱

@app.route("/classes")
def classes():
    return render_template("classes.html.jinja2")

@app.route("/contact")
def contact():
     return render_template("contact.html.jinja2")

@app.route("/traffic")
def traffic():
     return render_template("traffic.html.jinja2")

@app.route("/news")
def news():
     return render_template("news.html.jinja2")