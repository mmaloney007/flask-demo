# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from flask import Flask, render_template, request, redirect
import requests
import pandas as pd
from pandas import DataFrame,Series
import datetime as dt
import bokeh
from bokeh.palettes import Spectral11
from bokeh.plotting import figure, show, output_file
from bokeh.embed import components
#import os

################################################################################
# secret data kept in separate file
def loadApiKey( keyFile, keyName ) :
     print "in loadApiKey"	
     with open(keyFile) as f:
		fromFile = {}
		for line in f:
			line = line.split() # to skip blank lines
			if len(line)==3 :			# 
				fromFile[line[0]] = line[2]			
     f.close()
     apiKey = fromFile[keyName]
     print "leaving loadApiKey"
     return apiKey

################################################################################
# API KEY SEPERATED FOR SECURITY
def fetch_quandl(ticker, apiKey) :

	ticker = ticker.upper()
      # FIGURE OUT 30 DAYS
	now = dt.datetime.now().date()
	then = now - dt.timedelta(days=30)
	then = "&start_date=" + then.strftime("%Y-%m-%d")
	now  = "&end_date=" + now.strftime("%Y-%m-%d")

	reqUrl = 'https://www.quandl.com/api/v3/datasets/WIKI/' + ticker + \
					'.json?api_key=' + apiKey + now + then
     # LOG URL
	print reqUrl

	r = requests.get(reqUrl)

     # ENSURE DATA IS VALID
	if r.status_code < 400 :
		# get name of company
		name = r.json()['dataset']['name']
		name = name.split('(')[0]

		# get data
           # GIVE DATA AN INDEX
		dat = r.json()['dataset']
		df = DataFrame(dat['data'], columns=dat['column_names'] )
		df = df.set_index(pd.DatetimeIndex(df['Date']))

	else :
		print "Stock ticker not valid"
		df = None
		name = None

	return df, name

################################################################################
# MAKE PLOT FOR PLOT.HTML
def make_figure(df, tickerText ):

    #output_file("legend.html")
    # SEPERATE OUT DATE FOR PLOTTING ON ONE CHART    
    x = df.index.get_values()
    y = df['Close']
    z = df['Open']
    a = df['High']
    b = df['Low']

    p = figure(x_axis_type="datetime", width=800, height=600)
    p.title = "Symbol: " + tickerText + " Prices"
    p.circle(x, y, color='navy', legend='Close', size=10)
    p.circle(x, z, color='red', legend='Open', size=10)
    p.line(x, a, color='red', legend='High', alpha=0.5)
    p.line(x, b, color='black', legend='Low', alpha=0.5)

    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Price'
    p.legend.orientation = "vertical"
    
    #TEST CODE 
    #show(p)

    if 0:
	bokeh.io.output_file('templates/plotstock.html')
	bokeh.io.save(p)

    script, div = components(p)
    return script, div

################################################################################

app = Flask(__name__)

# init
app.vars = {}
# LOCATION OF SECURE KEY
keyFile = 'API_KEYS'
# KEY FOR QUANDL
keyName = 'quandl'
# LOAD API KEY
app.vars['apiKey'] = loadApiKey( keyFile, keyName)

# ROUTE APP TO INDEX
@app.route('/')
def main():
	return redirect('/index')

# INDEX.HTML REDIRECTION
@app.route('/index', methods=['GET','POST'])
def index():
	return render_template('index.html')

# START THE PLOT PAGE
@app.route('/plotpage', methods=['POST'])
def plotpage():
	tickStr = request.form['tickerText']
	#reqList = request.form['priceCheck'] # checkboxes

	app.vars['ticker'] = tickStr.upper()
	#app.vars['priceReqs'] = reqList

	df,name = fetch_quandl(app.vars['ticker'], app.vars['apiKey'])


	# if the stock ticker isn't valid, reload with warning message
	if not type(df) == DataFrame :
		msg = "Sorry, that ticker isn't valid. Please try again."
		return render_template('index.html', msg=msg)
	else:
          script, div = make_figure(df, app.vars['ticker'])
          return render_template('plot.html', script=script, div=div, ticker=name)

# SWITCH PORT FOR HEROKU                    
if __name__ == '__main__':
    app.run(port=33507)