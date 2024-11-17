import csv
import json

import pandas as pd
import yfinance as yf

from datetime import datetime
from dateutil.parser import parse

from .stock_data import StockData


class Utils:

    @staticmethod
    def save_SP500_list(raw_path: str, save_path: str) -> None:

        tickers = []

        with open(raw_path, "r") as f:

            reader = csv.reader(f)
            next(reader)

            for row in reader:

                tickers.append(row[0])

        with open(save_path, "w") as f:

            json.dump(tickers, f, indent=4)

    @staticmethod
    def load_SP500_list(path: str) -> list[str]:

        tickers = []

        with open(path, "r") as f:

            tickers = json.load(f)

        return tickers

    @staticmethod
    def find_closer_date(date1: datetime, date2: datetime, ref: datetime) -> datetime:

        date1_diff = abs(ref - date1)
        date2_diff = abs(ref - date2)

        return date1 if date1_diff < date2_diff else date2

    @staticmethod
    def format_data(stock_data: StockData) -> StockData:

        formatted = stock_data.data[["t", "o", "h", "l", "c", "v"]]
        formatted.columns = ["date", "open", "high", "low", "close", "volume"]
        formatted.loc[:, "date"] = formatted["date"].apply(lambda x: parse(x).date())

        return StockData(ticker=stock_data.ticker, data=formatted)

    @staticmethod
    def get_split_dates(ticker: str, start_date: str, end_date: str) -> pd.Series:

        split_dates = yf.Ticker(ticker).splits
        split_dates.index = pd.to_datetime(split_dates.index).strftime("%Y-%m-%d")
        split_dates = split_dates[
            (start_date <= split_dates.index) & (split_dates.index <= end_date)
        ]

        return split_dates

    @staticmethod
    def adjust_for_stock_splits(
        stock_data: StockData, split_dates: pd.Series
    ) -> StockData:

        prod = 1
        last_split_date = datetime(1900, 1, 1)
        targets = ["open", "high", "low", "close"]

        for ratio in split_dates.values:

            prod *= ratio

        for split_date, ratio in split_dates.items():

            for target in targets:

                stock_data.data.loc[
                    (last_split_date <= pd.to_datetime(stock_data.data["date"]))
                    & (pd.to_datetime(stock_data.data["date"]) < split_date),
                    target,
                ] /= prod

            prod /= ratio
            last_split_date = split_date

        return stock_data

    @staticmethod
    def make_ordered_pair(str1: str, str2: str):

        return (str1, str2) if str1 < str2 else (str2, str1)
