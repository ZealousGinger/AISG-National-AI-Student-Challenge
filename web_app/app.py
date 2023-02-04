import sqlite3
from flask import Flask, config, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly
import plotly.express as px
import json


app = Flask(__name__)

@app.route('/callback', methods=['POST', 'GET'])
def cb():
    return gm(request.args.get('data'))

def get_db_connection():
    conn = sqlite3.connect('bus.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM bustable').fetchall()
    df = pd.read_sql_query("SELECT * FROM bustable", conn)
    df["datetime_split"] =df["datetime"].str.split(" ")
    df["date"] = df["datetime_split"].str[0]
    x = df.groupby('date', as_index=False, sort=False).sum()
    plt.clf()
    plt.rcParams['figure.figsize'] = [20,20]
    plt.rc('ytick', labelsize=14) 
    plt.rc('xtick', labelsize=9) 
    plt.plot(x['date'], x['count'], color='red', marker='o')
    plt.title('count vs date', fontsize=14)
    plt.xlabel('date', fontsize=9)
    plt.ylabel('count', fontsize=14)
    plt.grid(True)
    plt.savefig('static/foo.jpg')
    conn.close()
    return render_template('index.html', posts=posts)


def gm(date='2023-02-03'):
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM bustable').fetchall()
    df = pd.read_sql_query("SELECT * FROM bustable", conn)
    x = df.groupby('datetime', as_index=False, sort=False).sum()
    x["datetime_split"] =x["datetime"].str.split(" ")
    x["date"] = x["datetime_split"].str[0]
    x["time"] = x["datetime_split"].str[1]
    fig = px.line(x[x['date']==date], x="time", y="count")
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    print(fig.data[0])
    return graphJSON

if __name__ == '__main__':
    app.run(debug=False,port=4996)