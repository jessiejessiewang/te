import logging

import pandas as pd

from .data_loader import query_ret


class ReturnsCovRiskModel(object):

    def __init__(self, tickers: list, start_date: pd.Timestamp, end_date: pd.Timestamp, **kwargs) -> None:
        """
        :param tickers: list of universe
        :param start_date: start date
        :param end_date: end date
        :param kwargs: other attributes for cp.FullSigma interface
        """
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date

    def get_value(self):
        """
        Get risk model
        """
        logging.info("built risk model from %s to %s" % (self.start_date, self.end_date))
        returns = query_ret(self.tickers, self.start_date, self.end_date)

        # Barra risk model in practice
        return_cov = returns.rolling(window=250, min_periods=250).cov().dropna().droplevel(1)
        return return_cov
