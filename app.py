from flask import Flask, request
from utils import *
import pandas as pd
app = Flask("forecasting api")

@app.route('/forecast')
def forecast_price():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    num_guests = request.args.get("num_guests")
    num_bedrooms = request.args.get("num_bedrooms")
    num_beds = request.args.get("num_beds")
    zipcode = request.args.get("zipcde")
    min_review = request.args.get("min_review")
    return {"hello":"world", "test": 2}

@app.route('/update')
def update_data():
    return 'Hello, World!'