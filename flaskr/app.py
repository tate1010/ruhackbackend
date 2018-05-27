import pandas as pd
import numpy as np
import scipy as sp
import scipy.stats
from flask import Flask
import os
from matplotlib import pyplot as plt
from pprint import pprint
import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta, MO
from flask import jsonify

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
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
            return jsonify(result)

    return app
