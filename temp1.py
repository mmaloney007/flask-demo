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
from bokeh.plotting import figure, show
from bokeh.embed import components

reqUrl = 'https://www.quandl.com/api/v3/datasets/WIKI/AAPL.json?api_key=kA9d2yWTvUf8x-SW2xSo&end_date=2016-08-30&start_date=2016-07-31'

r = requests.get(reqUrl)

if r.status_code < 400 :
		# get name of company
		name = r.json()['dataset']['name']
		name = name.split('(')[0]

		# get data
		dat = r.json()['dataset']
		df = DataFrame(dat['data'], columns=dat['column_names'] )
		df = df.set_index(pd.DatetimeIndex(df['Date']))

else :
		print "Stock ticker not valid"
		df = None
		name = None
  
print df.to_string(index=False)

x = df.index.get_values()

y = df['Close']

x = df.index.get_values()

y = df['Close']

#df['Date']
#df['Close']
  
p = figure(x_axis_type="datetime", width=800, height=600)
p.title = "APPL Prices"
p.line(x, y, color='navy', alpha=0.5)

p.xaxis.axis_label = 'Date'
p.yaxis.axis_label = 'Price'
p.legend.orientation = "vertical"

   
show(p)