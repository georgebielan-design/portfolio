import csv
import yfinance as yf
import os

print("Portfolio Rebalancer: Sample QQQ-style portfolio using CSV\n")

# ------------------------------------------------------------
# 1. Load holdings and raw weights from CSV
# ------------------------------------------------------------

current_holdings = {}    # ticker -> shares
raw_weights = {}         # ticker -> raw weight (percentage, not normalized)
cash_raw_weight = 0.0    # raw weight for cash row

csv_path = "qqq_holdings.csv"   # CSV must be in same folder as main.py

# Validate that CSV exists
if not os.path.exists(csv_path):
    raise FileNotFoundError(
        f"Could not find {csv_path}. Make sure it is in the same folder as main.py"
    )

with open(csv_path, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        ticker = row["Ticker"].strip().upper()
        raw_weight = float(row["RawWeight"])

        if ticker == "CASH":
            cash_raw_weight = raw_weight
        else:
            shares = float(row["Shares"])
            current_holdings[ticker] = shares
            raw_weights[ticker] = raw_weight

# Sample cash balance for demonstration (NOT your real portfolio)
cash_balance = 5000.0

print("Loaded from CSV:")
print("  Current Holdings (shares):")
for t, s in current_holdings.items():
    print(f"    {t}: {s}")

print("\n  Raw Weights from CSV:")
for t, w in raw_weights.items():
    print(f"    {t}: {w}%")

print(f"\n  Cash Balance (sample): ${cash_balance:,.2f}\n")


# ------------------------------------------------------------
# 2. Normalize raw weights (to sum to 1.0)
# ------------------------------------------------------------

total_raw = sum(raw_weights.values()) + cash_raw_weight

target_weights = {t: w / total_raw for t, w in raw_weights.items()}
target_weights["CASH"] = cash_raw_weight / total_raw

print("Normalized Target Weights:")
for t, w in target_weights.items():
    print(f"    {t}: {w:.2%}")
print()


# ------------------------------------------------------------
# 3. Fetch current prices using yfinance
# ------------------------------------------------------------

prices = {}
print("Fetching current prices...\n")

for ticker in current_holdings:
    try:
        data = yf.Ticker(ticker).history(period="1d")
        price = float(data["Close"][0])
        prices[ticker] = price
    except Exception:
        prices[ticker] = 0.0
        print(f"    Warning: Could not fetch price for {ticker}")

print("Current Prices:")
for t, p in prices.items():
    print(f"    {t}: ${p:.2f}")
print()


# ------------------------------------------------------------
# 4. Compute total portfolio value (stocks + cash)
# ------------------------------------------------------------

stock_value = sum(current_holdings[t] * prices[t] for t in current_holdings)
portfolio_value = stock_value + cash_balance

print(f"Stock Value: ${stock_value:,.2f}")
print(f"Cash Balance: ${cash_balance:,.2f}")
print(f"Total Portfolio Value: ${portfolio_value:,.2f}\n")


# ------------------------------------------------------------
# 5. Compute current weights
# ------------------------------------------------------------

current_weights = {}
for t, shares in current_holdings.items():
    if prices[t] == 0:
        continue
    current_weights[t] = (shares * prices[t]) / portfolio_value

current_weights["CASH"] = cash_balance / portfolio_value

print("Current Weights:")
for t, w in current_weights.items():
    print(f"    {t}: {w:.2%}")
print()

# ------------------------------------------------------------
# 6. Compute rebalance trades (turnover + min trade size + rounding + CSV export)
# ------------------------------------------------------------

MAX_TURNOVER = 0.05       # 5% turnover limit
MIN_TRADE_DOLLARS = 100.0 # ignore trades under $100 (after scaling)

print("Rebalance Trade Tickets (turnover + min-size + rounding):\n")

# First pass: compute raw trades (no filters yet)
raw_trades = []   # (ticker, action, shares, price, dollar_amount)

for t, target_weight in target_weights.items():
    if t == "CASH":
        continue

    if prices[t] == 0:
        continue

    target_value = target_weight * portfolio_value
    current_value = current_holdings[t] * prices[t]
    dollar_diff = target_value - current_value
    shares_diff = dollar_diff / prices[t]

    if abs(shares_diff) < 0.01:
        continue

    action = "BUY" if shares_diff > 0 else "SELL"
    raw_trades.append((t, action, abs(shares_diff), prices[t], abs(dollar_diff)))

# Calculate total raw turnover
total_turnover = sum(trade[4] for trade in raw_trades) / portfolio_value

print(f"Raw turnover: {total_turnover:.2%}")
print(f"Max allowed turnover: {MAX_TURNOVER:.2%}")

# Scale all trades if turnover exceeds limit
scale_factor = 1.0
if total_turnover > MAX_TURNOVER and total_turnover > 0:
    scale_factor = MAX_TURNOVER / total_turnover
    print(f"\nTurnover exceeds limit. Scaling all trades by factor: {scale_factor:.4f}\n")
else:
    print("\nTurnover is within limit. No scaling applied.\n")

# Table output header
print(f"{'Ticker':<8} {'Action':<6} {'Shares':>10} {'Price':>12} {'Dollar Amt':>15}")
print("-" * 55)

final_trades = []  # will save final, rounded trades for CSV export
skipped_small = 0
skipped_zero = 0

for (t, action, shares_diff, price, dollar_amt) in raw_trades:
    # apply scaling
    scaled_shares = shares_diff * scale_factor
    scaled_dollars = dollar_amt * scale_factor

    # apply minimum trade size on scaled dollars
    if scaled_dollars < MIN_TRADE_DOLLARS:
        skipped_small += 1
        continue

    # round to whole shares
    rounded_shares = round(scaled_shares)

    # skip if rounding wipes out the trade
    if rounded_shares == 0:
        skipped_zero += 1
        continue

    # recompute dollar amount based on rounded shares
    rounded_dollars = rounded_shares * price

    # print row
    print(
        f"{t:<8} {action:<6} {rounded_shares:>10} "
        f"{price:>12.2f} {rounded_dollars:>15.2f}"
    )

    # save for CSV export
    final_trades.append((t, action, rounded_shares, price, rounded_dollars))

print(f"\nTrades skipped (min trade size): {skipped_small}")
print(f"Trades skipped (rounded to zero): {skipped_zero}")

# ------------------------------------------------------------
# 7. Export final trades to CSV
# ------------------------------------------------------------

output_path = "rebalance_orders_sample.csv"

with open(output_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Ticker", "Action", "Shares", "Price", "DollarAmount"])

    for t, action, shares, price, dollar_amt in final_trades:
        writer.writerow([
            t,
            action,
            shares,
            f"${price:,.2f}",
            f"${dollar_amt:,.2f}"
        ])

