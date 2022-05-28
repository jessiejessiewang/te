import logging
import os.path
import pathlib

import pandas as pd
import yfinance
from contexttimer import Timer
from joblib import Memory
from singleton_decorator import singleton

mem = Memory(location='~/.cache', verbose=1)


@singleton
class DBConn(object):

    def __init__(self):
        logging.info("connected to yahoo finance database")
        try:
            self._conn = yfinance  # in practice, this is a database connection, use Yahoo finance to mock
        except Exception as e:
            logging.error('failed to connect yahoo finance, %s' % e)

    def get_conn(self):
        return self._conn


@mem.cache  # avoid repeated queries to exceed calls limit
def query(tickers: list, start_date: pd.Timestamp, end_date: pd.Timestamp,
          column: str):
    """
    Query market data from db
    :param tickers: list of universe
    :param start_date: start date of the query
    :param end_date: end date of the query
    :param column: selected column from the table
    :return: dataframe contains the queried data, or raise exception from db
    """
    conn = DBConn().get_conn()
    with Timer() as t:
        df = conn.download(tickers, start=start_date, end=end_date)[column]
    assert not df.empty, 'Database returns invalid %s data' % column
    logging.info(
        "loaded {} rows from yfinance within {:.3f}".format(len(df), t.elapsed))
    return df


def query_ret(tickers: list, start_date: pd.Timestamp, end_date: pd.Timestamp):
    """
    Query return
    :param tickers: list of universe
    :param start_date: start date of the query
    :param end_date: end date of the query
    :return: dataframe contains the queried data, or raise exception from db
    """
    price = query(tickers, start_date, end_date, column='Adj Close')
    returns = price / price.shift(1) - 1
    # add cash asset return, should be risk free interest
    returns['cash'] = 0
    return returns.fillna(0)


def query_trd_value(tickers: list, start_date: pd.Timestamp,
                    end_date: pd.Timestamp):
    """
    Query traded value
    :param tickers: list of universe
    :param start_date: start date of the query
    :param end_date: end date of the query
    :return: dataframe contains the queried data, or raise exception from db
    """
    volume = query(tickers, start_date, end_date, column='Volume')
    price = query(tickers, start_date, end_date, column='Close')
    return volume * price


def query_universe(index='S&P100'):
    """

    :param index: index name, in practice this comes from database or bloomberg terminal
    :return: dataframe contains the constituents
    """
    return pd.read_csv(f"{pathlib.Path(os.path.dirname(__file__))}/{index}.csv")


if __name__ == '__main__':
    univ = query_universe(index='S&P100')
    close = query(univ.Symbol.tolist(), pd.Timestamp(2017, 1, 1), pd.Timestamp(2021, 10, 22), column='Volume')  # Volume
    print(close)
