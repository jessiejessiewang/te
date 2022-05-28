import cvxportfolio as cp
import pandas as pd

from .risk_model import ReturnsCovRiskModel
from .signals import MomentumReturnsForecast


class Optimizer(cp.SinglePeriodOpt):
    def __init__(self, tickers: list, start_date: pd.Timestamp, end_date: pd.Timestamp, lambda_risk: float,
                 leverage_limit: int, max_weights: float, min_weights: float, adv_limit: float, half_spread: float,
                 borrow_costs: float) -> None:
        """
        :param tickers: list of universe
        :param start_date: start date
        :param end_date: end date
        :param lambda_risk: risk aversion ratio
        :param leverage_limit: leverage limit
        :param max_weights: max weight for each ticker
        :param min_weights: min weight for each ticker
        :param adv_limit: adv limit
        :param half_spread: bid-ask spread cost in transaction cost model, could contain fees
        """
        return_forecast = MomentumReturnsForecast(tickers, start_date, end_date).get_value()
        risk_model = ReturnsCovRiskModel(tickers, start_date, end_date).get_value()

        # can add execution cost, borrow fee
        tcost_model = cp.TcostModel(half_spread=half_spread)
        bcost_model = cp.HcostModel(borrow_costs=borrow_costs / 250)

        costs = [lambda_risk * cp.FullSigma(risk_model), tcost_model,
                 bcost_model]  # fit into cp format

        # average_volume = query_trd_value(tickers, start_date, end_date)
        constraints = [
            cp.DollarNeutral(),
            cp.LeverageLimit(leverage_limit),
            cp.MaxWeights(max_weights),
            cp.MinWeights(min_weights),
            # cp.MaxTrade(average_volume, adv_limit)  # ADV limit
        ]
        super().__init__(return_forecast, costs, constraints)
