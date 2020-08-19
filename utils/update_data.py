#!/usr/bin/python
import numpy as np
import pandas as pd
import requests
import bs4
import csv
from bs4 import BeautifulSoup

# This function is going to be used to accesss the newest data that we dont have
# able to pass in the date that we want the new data from in the string '0000-00-00' format
def get_latest_calendar(date='2020-11-20'):
    # the website we need to access to get the data
    bnbdata = "http://insideairbnb.com/get-the-data.html"
    # requesting to access the website
    page = requests.get(bnbdata)
    # using BeautifulSoup package as an HTML  parser
    soup = BeautifulSoup(page.content, 'html.parser')

    # finding the San Diego data table on the website and creating a list of csv file links
    table = soup.find("table", class_="table table-hover table-striped san-diego").find_all('a')

    # need to convert the HTML language into just plain links which is stored in results
    result = []
    for i in table:
        result.append(i.get("href"))

    # we need to be able to access the calendar.csv file from the page which will always be in the first index of the list because it would be the most up to date data
    latest_calendar_df = pd.read_csv(result[1])
    # accessing all the listings that we want to find the data for in calendar.csv
    listing_df = pd.read_csv(r'../data/listings.csv')
    # creating a hash set of all the unique ids within the listings.csv
    idset = set(listing_df.id.unique())
    # deleting all the rows that do not have the listing ids listed in idset
    latest_calendar_df = latest_calendar_df[latest_calendar_df.listing_id.isin(idset)]

    # finding all the unique dates that exist in the calendar dataframe
    arr2 = latest_calendar_df.date.unique()
    # only need data that is past the date of 2020-11-19 so needed to find the index of the '2020-11-20'
    index = np.where(arr2 == date)
    # making a set with the dates that we will be able to use because it is all the new data we dont have
    arr2 = set(arr2[index[0][0]:])
    # delete all the rows that do not have the need data
    latest_calendar_df = latest_calendar_df[latest_calendar_df.date.isin(arr2)]
    # reindex the new dataframe which has all the new data within it
    latest_calendar_df = latest_calendar_df.reset_index(drop=True)
    return latest_calendar_df

