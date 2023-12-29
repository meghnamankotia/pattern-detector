import yfinance as yf
import os,csv
import pandas as pd
import talib
import plotly.graph_objects as go
import plotly.io as pio
from flask import Flask,render_template,request
from patterns import patterns
from datetime import datetime, timedelta

app= Flask(__name__)

#home screen
@app.route('/')
def index():
    #return pattern entered in form
    pattern = request.args.get('pattern',None)
    stocks={}

    #create dictionary with stock symbols, values will be company, pattern and chart
    with open('datasets/companies.csv') as f:
        for row in csv.reader(f):
            stocks[row[5].split('.')[0]]={'company': row[0]}

    #check for pattern using talib and enter into dictionary
    if pattern:
        dataf= os.listdir('datasets/daily')
        for file in dataf:
            symbol= file.split('.')[0]
            try:
                df = pd.read_csv('datasets/daily/{}'.format(file))
                pattern_func= getattr(talib ,pattern)
                res= pattern_func(df['Open'],df['High'],df['Low'],df['Close'])
                last= res.tail(n=3).values[0]
                if last>0:
                    stocks[symbol][pattern]='bearish'
                elif last<0:
                    stocks[symbol][pattern]='bullish'
                else:
                    stocks[symbol][pattern]=None
            except:
                pass
            fig= go.Figure(go.Candlestick(x=df['Date'],open=df['Open'],low=df['Low'],high=df['High'],close=df['Close']))
            div_str=fig.to_html(include_plotlyjs=False, full_html= False)
            stocks[symbol]['chart']=div_str
    return render_template('index.html',patterns=patterns,stocks=stocks, current_pattern=pattern)

#load data into csv
@app.route('/snapshot')
def snapshot():
    with open('datasets/companies.csv') as f:
        companies = f.read().splitlines()
        for company in companies:
            symbol = company.split(',')[5]
            df= yf.download(symbol, start= datetime.today()-timedelta(days=30), end=datetime.today())
            df.to_csv('datasets/daily/{}.csv'.format(symbol.split('.')[0]))
    return {
        'case':'success'
    }