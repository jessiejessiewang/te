import logging

import cvxportfolio as cp
import pandas as pd
from dateutil.relativedelta import relativedelta

from .data_loader import query


class TradeEngine(object):

    def __init__(self, portfolio_id: str, tickers: list, policy: cp.policies.BasePolicy) -> None:
        """
        Trading Engine taking signals to re-balance and generate orders
        :param portfolio_id: portfolio id to retrieve positions from PMS and send orders to OMS
        :param tickers: list of universe (could be a security master in practice, including tickers reference)
        :param policy: re-balance policy/rule
        """
        logging.info("initialized Trade Engine")
        self.portfolio_id = portfolio_id
        self.tickers = tickers
        self.policy = policy

    def get_prices(self, t: pd.Timestamp):
        """
        Get close price
        :param t: point-in-time
        :return: close price for a specific day
        """
        return query(self.tickers, t - relativedelta(days=5), t + relativedelta(days=5), column='Close').loc[t]

    @staticmethod
    def get_lot_size():
        """
        Get lot size
        :return: lot size value
        """
        return 100  # a mocked number

    def get_trades(self, portfolio: pd.Series, t: pd.Timestamp):
        """
        Get optimized trades, given optimization policy and holding
        :param t: point-in-time
        :param portfolio: series of initial holdings
        :return: series, target trades for each ticker
        """
        return self.policy.get_trades(portfolio, t)

    def get_targets(self, portfolio: pd.Series, t: pd.Timestamp):
        """=
        Get target position
        :param t: point-in-time
        :param portfolio: series of initial holdings
        :return: series, target positions for each ticker
        """
        return self.get_trades(portfolio, t) + portfolio

    def get_orders(self, portfolio: pd.Series, t: pd.Timestamp):
        """
        Wrap up orders to send to Prime
        :param t: point-in-time
        :param portfolio: series of initial holdings
        :return: formatted order sheet
        """
        trades = self.get_trades(portfolio, t).iloc[:-1]

        # order size rounding
        orders = (trades / self.get_prices(t) / self.get_lot_size()).round() * self.get_lot_size()
        holding_shares = (portfolio / self.get_prices(t) / self.get_lot_size()).round() * self.get_lot_size()
        orders_list = orders.to_frame('quantity').join(holding_shares.to_frame('sop')) \
            .fillna({'sop': 0, 'quantity': 0})  # merge with current holdings

        # adapt to broker engine format
        orders_list = orders_list.reset_index().rename(columns={'index': 'symbol'})
        orders_list['security_type'] = 'EQUITY'  # could be FUTURES or others
        orders_list['side'] = ['SHORTSELL' if (q < 0 and abs(q) > s) else ('SELL' if q < 0 else 'BUY') for q, s in
                               zip(orders_list.quantity, orders_list.sop)]
        orders_list['order_type'] = 'MKT'  # MKT or LMT orders
        orders_list['algo'] = 'VWAP'  # execution algorithm, could be an object with more parameters
        orders_list['broker'] = 'JPM'  # decides the account to trade
        orders_list['portfolio_id'] = self.portfolio_id

        # to track order in case of cancel
        orders_list['order_id'] = [hash(self.portfolio_id + s + b + str(pd.Timestamp.now())) for s, b in
                                   zip(orders_list.symbol, orders_list.broker)]
        orders_list['batch_id'] = hash(self.portfolio_id + str(pd.Timestamp.now()))
        # ...

        return orders_list[['symbol', 'quantity', 'security_type', 'side', 'order_type', 'algo', 'broker',
                            'portfolio_id', 'order_id', 'batch_id']]