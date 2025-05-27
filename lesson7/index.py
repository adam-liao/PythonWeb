from flask import Flask,render_template
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import OperationalError

# 載入 .env 檔案
load_dotenv()
conn_string = os.getenv('RENDER_DATABASE')



from flask import Flask,render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html.jinja2")

@app.route("/classes")
def classes():
    name = "LIAO CHUN CHING"
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    return render_template("classes.html.jinja2",name=name,weekdays=weekdays)

    # name = "Robert"
    # return render_template("classes.html.jinja2",name=name)


@app.route("/new")
def new():
    try:
        conn = psycopg2.connect(conn_string)
        # raise Exception("出現錯誤")
        print("Connection established")
    except OperationalError as e:
        print("Connection failed")
        print()
        return render_template("error.html.jinja2",error_message="資料庫錯誤"),500
    except:
        return render_template("error.html.jinja2",error_message="不知名的錯誤"),500
        
    conn.close()
    return render_template("new.html.jinja2")

@app.route("/traffic")
def traffic():
    return render_template("traffic.html.jinja2")

@app.route("/contact")
def contact():
    return render_template("contact.html.jinja2")

