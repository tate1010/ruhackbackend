import pandas as pd
import numpy as np
import scipy as sp
import scipy.stats
from flask import Flask
from flask import request
import os
from pprint import pprint
import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta, MO
from flask import jsonify
import urllib.request
import urllib
import json

#def create_app(test_config=None):
    # create and configure the app

#    return app

app = Flask(__name__, instance_relative_config=True)
#app.config.from_mapping(
#    SECRET_KEY='dev',
#    DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
#)
#
#if test_config is None:
    # load the instance config, if it exists, when not testing
#    app.config.from_pyfile('config.py', silent=True)
#else:
    # load the test config if passed in
#    app.config.from_mapping(test_config)

# ensure the instance folder exists
#try:
#    os.makedirs(app.instance_path)
#except OSError:#
#    pass


@app.route('/')
def parse():
    key="AIzaSyB8QIFggqzXTSoUU3qD0oN_6aXxe64ZewU"
    keywords = {
        "radius":"1000"
    }
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?key=AIzaSyB8QIFggqzXTSoUU3qD0oN_6aXxe64ZewU&'
    queryDict = {x:request.args.get(x) for x in request.args}
    for keyword in [item for item in keywords if item not in queryDict]:
        queryDict[keyword]=keywords[keyword]
    queryString = "&".join([key+"="+value for (key,value) in queryDict.items()])
    url = url + str(queryString)

    contents = json.load(urllib.request.urlopen(url.replace(" ", "%20")))

    return jsonify(contents)



@app.route('/hello')
def hello():
        df = pd.read_excel('spending.xlsx',skiprows= 1)
        budget = 100

        grouped = df.groupby("Label")

        food = grouped.get_group("food")


        luxrary = grouped.get_group("luxury")

        luxury_food = grouped.get_group("luxury-food")

        pprint(food)

        def mean_confidence_interval(data, confidence=0.95):
            a = 1.0*np.array(data)
            n = len(a)
            m, se = np.mean(a), scipy.stats.sem(a)
            h = se * sp.stats.t._ppf((1+confidence)/2., n-1)
            return m, m-h, m+h

        mean, lower , upper = mean_confidence_interval(food["DEBIT"])
        date_remaining = 6 -  (datetime.datetime.today().weekday())
        today = date.today()
        last_monday = today + relativedelta(weekday=MO(-1))
        print(last_monday)
        this_week_spending =  food.loc[food["DATE"]>= str(last_monday)]
        budget_remaining = budget - this_week_spending["DEBIT"].sum()
        budget_remaining = str(budget_remaining)
        result = {"budget_remaining" :  budget_remaining}
        queryresult = urllib.request(query(43.6576585,-79.3809904))
        return jsonify(result)

def query(lat,lon):
    radius = 200
    minprice = 0
    maxprice = 4
    key = "key=AIzaSyB8QIFggqzXTSoUU3qD0oN_6aXxe64ZewU"
    location= "location=" + str(lat) +","+ str(lon)
    radius = "radius=" + str(radius)
    minprice = "minprice=" + str(minprice)
    maxprice = "maxprice=" + str(maxprice)
    query = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?types=restaurant"
    query = appendquery(query,[key,location,radius])
    return query

def appendquery(q,item):
    for i in item:
        q =  q + "&" + i
    return q

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)

    # queryresult = json.load(urllib.request.urlopen(query(43.6576585,-79.3809904)))
