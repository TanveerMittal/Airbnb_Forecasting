import os
import bs4
import csv
import pickle
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from datetime import date, datetime,timedelta
from statsmodels.tsa.arima_model import ARIMA

def get_latest_calendar():
    """Function to scrape latest insideairbnb data"""
    # the website we need to access to get the data
    bnbdata = "http://insideairbnb.com/get-the-data.html"
    # Requesting to access the website
    page = requests.get(bnbdata)
    # Using BeautifulSoup package as an HTML  parser
    soup = BeautifulSoup(page.content, 'html.parser')

    # Finding the San Diego data table on the website and creating a list of csv file links
    table = soup.find("table", class_="table table-hover table-striped san-diego").find_all('a')

    # Need to convert the HTML language into just plain links which is stored in results
    result = []
    for i in table:
        result.append(i.get("href"))

    # We need to be able to access the calendar.csv file from the page which will always be in the first index of the list because it would be the most up to date data
    latest_calendar_df = pd.read_csv(result[1])
    # Accessing all the listings that we want to find the data for in calendar.csv
    listing_df = pd.read_csv(r'../data/listings.csv')
    # Creating a hash set of all the unique ids within the listings.csv
    idset = set(listing_df.id.unique())
    # Deleting all the rows that do not have the listing ids listed in idset
    latest_calendar_df = latest_calendar_df[latest_calendar_df.listing_id.isin(idset)]

    # Finding all the unique dates that exist in the calendar dataframe
    arr2 = latest_calendar_df.date.unique()
    # Only need data that is past the date of 2020-11-19 so needed to find the index of the '2020-11-20'
    index = np.where(arr2 == date)
    # Making a set with the dates that we will be able to use because it is all the new data we dont have
    arr2 = set(arr2[index[0][0]:])
    # Delete all the rows that do not have the need data
    latest_calendar_df = latest_calendar_df[latest_calendar_df.date.isin(arr2)]
    # Reindex the new dataframe which has all the new data within it
    latest_calendar_df = latest_calendar_df.reset_index(drop=True)
    return latest_calendar_df

# Cleans the listings csv and returns a new dataframe
def clean_listings(df_listings):
    # Select needed columns
    listings = df_listings[['id','accommodates','bedrooms','beds', 'zipcode', 'review_scores_rating']]
    return listings


def clean_calendar(df_calendar):
    """Cleans the calendar csv and returns a new dataframe"""
    # Select needed columns
    calendar = df_calendar[['listing_id','date','price']]
    # Drop rows with missing data
    calendar.dropna()
    # Convert price column to number
    calendar['price'] = calendar['price'].apply(dollar_to_number)
    # Convert data column to datetime object
    calendar['date'] = pd.to_datetime(calendar['date'])
    return calendar

def dollar_to_number(string):
    """Helper Function for clean_calendar"""
    string = string.replace('$', '')
    string = string.replace(',', '')
    string = string.replace('.', '')
    number = int(string)/100
    return number

# 
def filter_room_details(df_listings, num_guests, num_bedrooms, num_beds, area, review):
    """Returns a dataframe with rooms that meet parametes"""
    # Get rooms greater than max_num_guests
    df_filtered_room = df_listings[(df_listings['accommodates'] ==  num_guests)
                        & (df_listings['bedrooms']  >=  num_bedrooms)
                        & (df_listings['beds']  >=  num_beds)
                        & (df_listings['review_scores_rating']  >=  review)]
    # If area is given get rooms in area
    if area != 0:
        df_filtered_room = df_filtered_room.loc[df_filtered_room['zipcode']  ==  area]
    return df_filtered_room



def filter_timeseries(df_listings, df_calendar):
    """Returns a time series of prices for rooms that meet time critera"""
    # Get listing ids from df_listings
    id_list = df_listings['id'].to_list()
    
    # Remove ids from df_calendar that are not in id_list
    df_calendar_filtered = df_calendar[df_calendar['listing_id'].isin(id_list)]
        
    # Group items by date and find the average price on that day
    df_calendar_filtered = df_calendar_filtered.groupby(['date']).mean()
    
    # Convert and return as series
    series = pd.Series(df_calendar_filtered['price'])
    return series

def create_timeseries(df_listings, df_calendar, num_guests, start_date, end_date, min_num_bedrooms, min_num_beds, zipcode, minimum_review):
    """Creates time series given listing paramaters"""
    df_room_details = filter_room_details(df_listings, num_guests, min_num_bedrooms, min_num_beds, zipcode, minimum_review)
    timeseries = filter_timeseries(df_room_details, df_calendar)
    return timeseries

def forecast(ser, start_date, end_date):
    """Uses the ARIMA model to return the forecasted price 
    of a user's stay and a visualization of the prices
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