
import csv
import json
import math


# Load portfolio data
try:
    with open("portfolios.json", "r", encoding="utf-8") as file:
        portfolios = json.load(file)

except FileNotFoundError:
    print("Error: portfolios.json file not found.")
    raise SystemExit

except json.JSONDecodeError:
    print("Error: portfolios.json contains invalid JSON.")
    raise SystemExit


# Check each trade against the portfolio rules
def check_trade_compliance(trade, portfolio):

    security_id = trade["security_id"]
    action = trade["action"]

    # Validate quantity, price and action
    try:
        quantity = float(trade["quantity"])
        price = float(trade["price"])

        if (
            not math.isfinite(quantity)
            or not math.isfinite(price)
            or quantity <= 0
            or price <= 0
            or action not in ["Buy", "Sell"]
        ):
            return "Rejected", "Invalid trade data."

    except (ValueError, TypeError):
        return "Rejected", "Invalid trade data."

    # Check whether the security is restricted
    if security_id in portfolio["restricted_securities"]:
        return "Rejected", "Security is restricted for this portfolio."

    # Find the existing quantity of the security
    existing_quantity = 0

    for holding in portfolio["current_holdings"]:
        if holding["security_id"] == security_id:
            existing_quantity = holding["quantity"]
            break

    # Check whether enough holdings are available for selling
    if action == "Sell":

        if existing_quantity < quantity:
            return "Rejected", "Insufficient holdings to sell."

    # Check whether enough cash is available for buying
    if action == "Buy":

        trade_cost = quantity * price

        if trade_cost > portfolio["cash_balance"]:
            return "Rejected", "Insufficient cash for this buy order."

        # Calculate the portfolio value after the purchase
        post_trade_cash = portfolio["cash_balance"] - trade_cost

        post_trade_quantity = existing_quantity + quantity

        post_trade_value = post_trade_quantity * price

        # Calculate the value of all other holdings
        value_of_other_holdings = sum(
            holding["quantity"] * holding["market_price"]
            for holding in portfolio["current_holdings"]
            if holding["security_id"] != security_id
        )

        total_portfolio_value = (
            post_trade_cash
            + post_trade_value
            + value_of_other_holdings
        )

        # Calculate the position percentage
        if total_portfolio_value <= 0:
            position_pct = (
                0 if post_trade_value == 0 else float("inf")
            )
        else:
            position_pct = post_trade_value / total_portfolio_value

        # Check the maximum position limit
        if position_pct > portfolio["max_position_pct"]:
            return (
                "Needs Manual Sign-off",
                "Exceeds maximum position concentration — requires approval."
            )

    # Trade passed all compliance checks
    return "Approved", "Trade passed all compliance checks."


# Read proposed trades from the CSV file
try:
    with open("trades_test.csv", "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        required_columns = [
            "portfolio_id",
            "security_id",
            "action",
            "quantity",
            "price",
            "security_type"
        ]

        if reader.fieldnames is None or not all(
            column in reader.fieldnames for column in required_columns
        ):
            print("Error: trades_test.csv has missing or incorrect columns.")
            raise SystemExit

        trades = list(reader)

except FileNotFoundError:
    print("Error: trades_test.csv file not found.")
    raise SystemExit


# Process all proposed trades
results = []

for trade in trades:

    portfolio_id = trade["portfolio_id"]

    if portfolio_id not in portfolios:
        decision = "Rejected"
        reason = "Portfolio reference data not found."

    else:
        decision, reason = check_trade_compliance(
            trade,
            portfolios[portfolio_id]
        )

    results.append({
        "portfolio_id": portfolio_id,
        "security_id": trade["security_id"],
        "action": trade["action"],
        "quantity": trade["quantity"],
        "price": trade["price"],
        "security_type": trade["security_type"],
        "decision": decision,
        "reason": reason
    })


# Save the decisions in an output CSV file
fieldnames = [
    "portfolio_id",
    "security_id",
    "action",
    "quantity",
    "price",
    "security_type",
    "decision",
    "reason"
]

try:
    with open(
        "trade_compliance_results.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

except OSError as error:
    print("Error saving output file:", error)
    raise SystemExit


# Display individual trade decisions
print("\n========== TRADE COMPLIANCE RESULTS ==========\n")

for result in results:

    print("------------------------------------------")
    print("Portfolio ID :", result["portfolio_id"])
    print("Security ID  :", result["security_id"])
    print("Action       :", result["action"])
    print("Quantity     :", result["quantity"])
    print("Price        :", result["price"])
    print("Decision     :", result["decision"])
    print("Reason       :", result["reason"])


# Display the final summary
approved = sum(
    1 for result in results
    if result["decision"] == "Approved"
)

rejected = sum(
    1 for result in results
    if result["decision"] == "Rejected"
)

manual = sum(
    1 for result in results
    if result["decision"] == "Needs Manual Sign-off"
)

print("\n========== TRADE SUMMARY ==========")
print("Total Trades          :", len(results))
print("Approved Trades       :", approved)
print("Rejected Trades       :", rejected)
print("Needs Manual Sign-off :", manual)

print("\nResults saved in trade_compliance_results.csv")
