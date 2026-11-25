
# Portfolio Trade Order Compliance & Execution Checker

## 1. Problem Statement

Before executing portfolio trades, each proposed order must be checked to ensure it follows portfolio rules. These checks include valid trade details, restricted securities, available cash, sufficient holdings for selling, and maximum position concentration.

## 2. Solution

This project uses Python to validate proposed trades against portfolio reference data and generate a compliance report.

## 3. Implementation

- Trade details are read from `trades_test.csv` using Python's CSV module.
- Portfolio information is loaded from `portfolios.json` using the JSON module.
- Each trade is checked against the six compliance rules in the specified order.
- Buy orders are checked for available cash and maximum position concentration.
- Sell orders are checked for sufficient holdings.
- Each trade is assigned one of three decisions:
  - Approved
  - Rejected
  - Needs Manual Sign-off
- The final decisions and reasons are saved in `trade_compliance_results.csv`.

## 4. How to Run

Open the project folder in the terminal and execute:

```bash
python main.py
```

The output file `trade_compliance_results.csv` is generated automatically after successful execution.
