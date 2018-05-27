import pandas as pd
import numpy as np
import scipy as sp
import scipy.stats
from flask import  Flask, flash, redirect, render_template, request, session, abort, url_for
from flask import request
from flask_cors import CORS
import os
from pprint import pprint
import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta, MO
from flask import jsonify
import urllib.request
import urllib
import json
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


#def create_app(test_config=None):
    # create and configure the app

#    return app

app = Flask(__name__, instance_relative_config=True)
CORS(app)
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

df = pd.read_excel('spending.xlsx',skiprows= 1)
budget = 100
grouped = df.groupby("Label")
food = grouped.get_group("food")
# luxrary = grouped.get_group("luxury")
# luxury_food = grouped.get_group("luxury-food")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def parse():
    key="AIzaSyB8QIFggqzXTSoUU3qD0oN_6aXxe64ZewU"
    keywords = {
        "radius":"1000"
    }
    queryDict = {x:request.args.get(x) for x in request.args}
    for keyword in [item for item in keywords if item not in queryDict]:
        queryDict[keyword]=keywords[keyword]
    queryString = "&".join([key+"="+value for (key,value) in queryDict.items()])
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?key=AIzaSyDcQr1HHBaG-SzBkfue0sJDyOKcCQFqI4I'
    url = url + str(queryString)

    contents = json.load(urllib.request.urlopen(url.replace(" ", "%20")))

    try:
        next_page_token = contents["next_page_token"]
    except:
        pass
    contents  = contents["results"]
    l, h , allow = hello()
    globalid = []
    #return(jsonify(contents))
    for item in contents:


      try:
        if item["opening_hours"]["open_now"] == False:

            cur = {}
            if allow < 15 and item["price_level"] == 1:
                cur["rating"] = item["rating"]
                cur["location"] = (item["geometry"]["location"])
                cur["name"] = item["name"]

            elif allow > 15 and allow < 30 and item["price_level"] == 2:
                cur["rating"] = item["rating"]
                cur["location"] = (item["geometry"]["location"])
                cur["name"] = item["name"]
            else:
                cur["rating"] = item["rating"]
                cur["location"] = item["geometry"]["location"]
                cur["name"] = item["name"]


            globalid.append(cur.copy())


      except:
           pass


    return jsonify(globalid)



#/update?location=_x,_y
@app.route('/update')
def update():
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?type=restaurant&key=AIzaSyDcQr1HHBaG-SzBkfue0sJDyOKcCQFqI4Iradius=20&'
    url1 = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?type=cafe&key=AIzaSyDcQr1HHBaG-SzBkfue0sJDyOKcCQFqI4Iradius=20&'
    location = "location="+request.args.get("location")
    contents = json.load(urllib.request.urlopen(url+location))
    contents1 = json.load(urllib.request.urlopen(url1+location))
    contents = contents["results"]
    contents1 = contents1["results"]

    restaurants = [item["name"] for item in (contents+contents1)]
    #
    result = {}
    for item in restaurants:
        food_rest = 0.0
        food_type = item.lower()
        for meat in food.iterrows():
            if food_type in meat[1]["DESCRIPTION"].lower() or fuzz.partial_ratio(food_type.lower(), meat[1]["DESCRIPTION"].lower()) >= 75:
                food_rest = food_rest +  meat[1]["DEBIT"]

        if food_rest != 0.0:
            result[food_type] = food_rest
    return jsonify(result)






def hello():


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
        #print(last_monday)
        this_week_spending =  food.loc[food["DATE"]>= str(last_monday)]
        budget_remaining = budget - this_week_spending["DEBIT"].sum()
        next_mon = ((today + relativedelta(weekday=MO(1))) - today ).days
        allowance = budget_remaining / next_mon
        return lower, upper , allowance

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
