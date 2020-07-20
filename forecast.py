import os
import pickle
import numpy as np
from datetime import timedelta
import matplotlib.pyplot as plt
from statsmodels.tsa.arima_model import ARIMA

def forecast(ser, start_date, end_date):
    """ Function that uses the ARIMA model to return the forecasted
     price of a user's stay and a visualization of the prices
    """

    # Fit model to data before requested date
    history = ser[ser.index.date < start_date]
    arima_params = pickle.load(open(os.path.join("models", "ARIMA_params.pkl"), "rb+"))
    model = ARIMA(history, order=(9, 2, 6))
    results = model.fit(arima_params)
    
    # Calculate how many values we need to forecast
    duration = (end_date - start_date).days
    predictions = results.forecast(duration)[0]

    # Create plot of forecasted values with confidence interval
    month = timedelta(days=31)
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.suptitle("Airbnb Price Forecasts")
    plt.ylabel("Price($)")
    plot_start = start_date - 2 * month
    plot_end = end_date + month
    ax.plot(ser[(ser.index.date >= plot_start) & (ser.index.date <= plot_end)], c="r")
    results.plot_predict(plot_start, plot_end, ax=ax)
    ax.lines.pop(2)

    # Return computed price and the plot
    return np.sum(predictions), fig