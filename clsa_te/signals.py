import logging

import pandas as pd

from .data_loader import query_ret


class MomentumReturnsForecast(object):

    def __init__(self, tickers: list, start_date: pd.Timestamp, end_date: pd.Timestamp):
        """
        Momentum return forecast
        :param tickers:
        :param start_date:
        :param end_date:
        """
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date

    def get_value(self):
        """
        Get signal value
        """
        logging.info("built signals from %s to %s" % (self.start_date, self.end_date))
        returns = query_ret(self.tickers, self.start_date, self.end_date)
        returns = returns.rolling(window=250, min_periods=250).mean()  # .shift(1) if no cheating
        return returns.dropna(how='all').fillna(0)
