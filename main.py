import csv
from yahoo_fin import stock_info as si
import yfinance as yf
import pandas as pd
import time
import requests

yf.pdr_override()
# Headers for Yahoo Finance Rapid API requests
headers = {
    "X-RapidAPI-Key": "9049f36495msh43ef213475bdb24p10d7dbjsn667b94f93167",
    "X-RapidAPI-Host": "yahoo-finance15.p.rapidapi.com"
}
# Dictionary that stores stocks smaller than S&P500 (key: ticker, value: list containing industry and pe ratio)
smaller_stocks = {}
# Create files for both S&P500 and smaller stocks (will change later)
with open("/Users/nguyennhatle/PycharmProjects/stockscreening2.0/stocks_500.csv", 'w') as f:
    w_obj = csv.writer(f)
    w_obj.writerow(["Ticker", "Sector", "PE Ratio"])

with open("/Users/nguyennhatle/PycharmProjects/stockscreening2.0/smaller_stocs.csv", 'w') as f_obj:
    w_obj = csv.writer(f_obj)
    w_obj.writerow(["Ticker", "Sector", "PE Ratio"])


# Return the S&P500 PE Ratio by retrieving the ratios of 500 companies under S&P500 and divided by the number of
# companies (average)
def get_sp_500_ratio():
    # Use yfinance built in method tickers_sp500 to get the symbol of 500 tickers
    tickers = si.tickers_sp500()
    print(tickers)
    # Number of companies (count) and sum of the pe ratios (sum_pe)
    count = 0
    sum_pe = 0
    print(len(tickers))
    # iterate through all tickers found above
    for ticker in tickers:
        # URL for requesting PE ratio
        url_pe_ratio = "https://yahoo-finance15.p.rapidapi.com/api/yahoo/qu/quote/" + ticker
        # URL for requesting industry (sector)
        # url_sector = "https://yahoo-finance15.p.rapidapi.com/api/yahoo/qu/quote/" + ticker + "/asset-profile"
        # Requesting using url and headers
        response = requests.request("GET", url_pe_ratio, headers=headers)
        # r = requests.request("GET", url_sector, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # d = r.json()
            sp500_pe_ratio = data[0]['trailingPE']
            sector = yf.Ticker(ticker).info['sector']
            print(ticker, sector, sp500_pe_ratio)
            # sector = d['assetProfile']['sector']
            if sp500_pe_ratio is not None:
                sum_pe += sp500_pe_ratio
                count += 1
            time.sleep(1)
            # Add info to the S&P500 stocks csv
            with open('/Users/nguyennhatle/PycharmProjects/stockscreening2.0/stocks_500.csv', 'a') as file:
                w = csv.writer(file)
                w.writerow([ticker, sector, sp500_pe_ratio])

        else:
            continue
    # Return the average (S&P 500 PE ratio)
    return sum_pe / count


# Function that returns true if the PE ratio of the current stock is smaller than the S&P500 ratio
# Also stores the stock info to smaller_stocks library (for future reference)
def smaller_than_sp500(ticker):
    info = []
    url = "https://yahoo-finance15.p.rapidapi.com/api/yahoo/qu/quote/" + ticker
    url_sector = "https://yahoo-finance15.p.rapidapi.com/api/yahoo/qu/quote/" + ticker + "/asset-profile"
    response = requests.request("GET", url, headers=headers)
    r = requests.request("GET", url_sector, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data[0]['trailingPE'] < get_sp_500_ratio():
            d = r.json()
            info.append([data[0]['trailingPE'], d['assetProfile']['sector']])
            smaller_stocks[ticker] = info
            # Save the stock to the csv file
            save_smaller_stocks(ticker)
            return True
    return False


# Function that saves the smaller stocks info to the smaller_stocks csv
def save_smaller_stocks(ticker):
    with open('smaller_stocks.csv', 'a') as fileobj:
        write_obj = csv.writer(fileobj)
        write_obj.writerow([ticker] + smaller_stocks[ticker])


# Create a pandas data frame given a csv file
def make_data_frame(csv_file):
    data = pd.read_csv(csv_file)
    return data


# Save the given csv file as an excel file
def save_as_excel(filename):
    df = make_data_frame(filename + ".csv")
    excel_file = pd.ExcelWriter('./' + filename + ".xlsx")
    df.to_excel(excel_file, index=False)
    excel_file.save()


get_sp_500_ratio()
