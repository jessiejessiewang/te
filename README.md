# clsa-task

#### Overview

Construct a simple trading signal on the constituents of the S&P100 (that is, not the index), and then run it through a 
backtest. Present its PnL and relevant risk/reward metrics.

#### Signal

Note: The signal is purely momentum as described by Wikipedia. Please be aware we included T0 return within the 
momentum, so the signal is forward-looking 1 day, purpose is to show valuable signals is able to turn into pnl in later
optimization and back-test process.

#### Data sources

We fetch the price data through yfinance. The constituents of SP100 are downloaded as csv from Wikipedia. In practice, 
both of these can come from internal database or Bloomberg terminal.

#### Examples

We conduct our analysis with pandas and present it with 

* Example script - run_te.py, to present how orders generation work in live/production potentially 
* Example jupyter - to include back-test with visualization (plotly and pyfolio)

#### Assumptions

* The SP100 constituent is as of 2022.03 (latest on Wikipedia), the universe over the period of time is constant, with 
  the same constituents as those in the S&P 
* The period of time is from 2021.01.01 to present, but it can be set from anytime to anytime
* Again on signals, it is 1-year momentum with 1-day forward-looking, the forward-looking is to make signal contains 
  alpha
* Within the optimization, we build risk model and the risk model based on the rolling returns between constituents

