from flask import Flask
from utils import *
app = Flask("forecasting api")

@app.route('/forecast')
def forecast_price():
    return {"hello":"world", "test": 2}

@app.route('/update')
def update_data():
    return 'Hello, World!'