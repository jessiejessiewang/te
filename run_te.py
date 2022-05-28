import json
import logging
import sys

import pandas as pd

from clsa_te.data_loader import query_universe
from clsa_te.optimizer import Optimizer
from clsa_te.position_loader import PositionsLoader
from clsa_te.trade_engine import TradeEngine

if __name__ == '__main__':
    # setup logger
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    # read config and create TE
    cfg = json.load(open(sys.argv[1]))
    print(cfg)

    run_date = pd.Timestamp(2022, 5, 26)

    # get universe
    univ = query_universe(cfg['index'])
    tickers = univ.Symbol.tolist()

    # get holdings
    positions_loader = PositionsLoader('url://whatever.abc.com', cfg['portfolio_id'])
    holdings = positions_loader.query(tickers, t=run_date)
    print(holdings)

    # get signals
    optimizer = Optimizer(tickers, **cfg['opt_kwargs'])
    signals = optimizer.return_forecast
    print(signals)

    # construct TE and generate orders
    te = TradeEngine(cfg['portfolio_id'], tickers, optimizer)
    orders = te.get_orders(holdings, t=run_date)
    print(orders)
    orders.to_csv(sys.argv[2], index=False)
