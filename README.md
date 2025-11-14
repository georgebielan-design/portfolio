# portfolio
Personal, my theme. 

# George Bielan – Investment & Financial Modeling Portfolio

Welcome to my personal portfolio. This repository showcases my work in:

- Investment analysis
- Portfolio valuation & alternative investments
- Python-based financial modeling
- Data analytics & visualization
- Portfolio construction & risk analysis
- Automated trading and rebalancing systems (in progress)

This portfolio is a collection of projects I am building to demonstrate my skills in markets, valuation, and applied financial modeling.

More projects will be added soon.

## Sample QQQ-Style Rebalancing Engine (Python)

This project simulates a rules-based rebalancing process for a portfolio modeled on the Nasdaq-100 (Invesco QQQ®).

### What it does

- Reads the full QQQ constituent list and index weights from `qqq_holdings.csv`
- Normalizes raw ETF weights into target portfolio weights (including a cash sleeve)
- Pulls live market data via `yfinance`
- Calculates current portfolio value (stocks + cash) and current weights
- Computes the dollar and share differences required to move toward index weights
- Applies:
  - A maximum turnover constraint (e.g., 5% of portfolio value)
  - A minimum trade size filter (e.g., ignore trades under $100)
  - Whole-share rounding for realistic execution
- Outputs:
  - A console table of BUY/SELL trade tickets
  - A CSV file `rebalance_orders.csv` with final, executable trade instructions

### Files

```text
projects/
  portfolio-rebalancer/
    main.py              # Rebalancing engine
    qqq_holdings.csv     # QQQ constituents + sample shares + index weights
    rebalance_orders.csv # Generated trade tickets (created when main.py runs)

### Example Rebalance Output (rebalance_orders_sample.csv)

The file `rebalance_orders_sample.csv` provides a sample of the actual trade tickets produced by the engine.  
It reflects the exact parameters used in the current version of the model:

- **Turnover-limited rebalancing:** Maximum 5% portfolio turnover  
- **Minimum trade size:** Trades under **$100 notional** are skipped  
- **Whole-share execution:** All trades are rounded to whole shares  
- **Scaled orders:** If raw turnover exceeds the limit, all trades are proportionally scaled  
- **Live pricing:** Execution prices are pulled dynamically via `yfinance`  
- **Cash handling:** Residual weight allocated to “CASH” in the model and included in total portfolio value  

Each row in `rebalance_orders_sample.csv` includes:

- Ticker  
- BUY/SELL action  
- Rounded share quantity  
- Executable price (formatted to two decimals)  
- Total notional value of the trade (also two decimals)  

This file serves as a realistic example of what a production rebalancing engine would send to a trader, OMS, or brokerage API.

