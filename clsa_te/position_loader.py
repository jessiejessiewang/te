import logging

import numpy as np
import pandas as pd


class PositionsLoader(object):

    def __init__(self, conn_client_name: str, portfolio_id: str) -> None:
        """
        Position data loader initialization
        :param portfolio_id: portfolio identifier
        """
        logging.info("connected to position database %s " % conn_client_name)
        self.conn = conn_client_name  # normally positions is read from a Position management system
        self.portfolio_id = portfolio_id

    def query(self, tickers: list, t: pd.Timestamp = None) -> pd.Series:
        """
        Query position at time t
        :param tickers: list of universe
        :param t: point-in-time
        :return: series of positions with index as ticker, values of positions values (shares in practice)
        """
        logging.info("PositionsLoader loaded positions for %s on %s" % (self.portfolio_id, t))
        aum = 100e6
        d = np.random.dirichlet(np.ones(len(tickers) + 1), size=1)[0] * aum  # should be related to portfolio_id
        s = pd.Series(index=tickers + ['cash'], data=d, name=self.portfolio_id)
        return s


if __name__ == '__main__':
    pos_loader = PositionsLoader(conn_client_name='url://', portfolio_id='JW_EQ')
    pos = pos_loader.query(['AMZN', 'GOOGL', 'TSLA', 'AAPL'], pd.Timestamp(2017, 1, 1))
    print(pos)
