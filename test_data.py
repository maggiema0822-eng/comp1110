import json
import random
from datetime import datetime, timedelta

# File paths for test data
TRANSACTIONS_FILE = "transactions.json"
BUDGET_FILE = "budget_rules.json"

# Predefined categories for transaction generation
CATEGORIES = ["food", "transport", "shopping", "entertainment", "subscription", "other"]

# Sample descriptions for each category to make test data realistic
DESCRIPTIONS = {
    "food": ["Canteen lunch", "Dinner at restaurant", "Bubble tea", "Breakfast", "Hot pot", "Fast food"],
    "transport": ["MTR", "Bus", "Taxi", "Ferry", "Minibus"],
    "shopping": ["Clothes", "Supermarket", "Electronics", "Books", "Stationery"],
    "entertainment": ["Cinema", "KTV", "Board game cafe", "Concert ticket", "Theme park"],
    "subscription": ["Netflix", "Spotify", "YouTube Premium", "iCloud", "Gym membership"],
    "other": ["Unknown payment", "Miscellaneous", "Random purchase"]
}


def make_date(days_ago):
    """
    Generate a date string for a specified number of days before today.

    Args:
        days_ago (int): Number of days in the past (0 = today)

    Returns:
        str: Date in YYYY-MM-DD format
    """
    return (datetime.now().date() - timedelta(days=days_ago)).strftime("%Y-%m-%d")


def generate_test_data():
    """
    Generate a fixed set of test transactions that covers all major alert types:
    - Normal spending (within budget)
    - Daily food overspend
    - Consecutive overspend (2 days in a row)
    - Percentage alert (large transport spending)
    - Monthly shopping alert
    - Uncategorized transaction

    This is the standard test dataset for verifying all alert functionality.
    """
    transactions = [
        # normal spending - within budget limits
        {"date": make_date(6), "amount": 35.0, "category": "food",
         "description": "Canteen lunch", "note": "normal meal"},
        {"date": make_date(6), "amount": 12.0, "category": "transport",
         "description": "MTR", "note": ""},

        # daily food overspend (food total = 65 > 50)
        {"date": make_date(5), "amount": 30.0, "category": "food",
         "description": "Breakfast", "note": ""},
        {"date": make_date(5), "amount": 35.0, "category": "food",
         "description": "Dinner", "note": "daily food over budget"},

        # consecutive overspend (2 days in a row, food > 50 each day)
        {"date": make_date(4), "amount": 60.0, "category": "food",
         "description": "Hot pot", "note": "first consecutive overspend day"},
        {"date": make_date(3), "amount": 70.0, "category": "food",
         "description": "BBQ dinner", "note": "second consecutive overspend day"},

        # percentage alert (transport = 180, high share of total)
        {"date": make_date(2), "amount": 180.0, "category": "transport",
         "description": "Taxi", "note": "large transport spending"},

        # monthly shopping alert (260 > threshold 200)
        {"date": make_date(1), "amount": 260.0, "category": "shopping",
         "description": "Clothes", "note": "monthly shopping over budget"},

        # uncategorized transaction (category 'other' triggers warning)
        {"date": make_date(0), "amount": 25.0, "category": "other",
         "description": "Unknown payment", "note": "uncategorized"}
    ]

    # Corresponding budget rules for testing
    budget_rules = [
        {"category": "food", "period": "daily", "threshold": 50.0, "alert_type": "warning"},
        {"category": "transport", "period": "weekly", "threshold": 100.0, "alert_type": "warning"},
        {"category": "shopping", "period": "monthly", "threshold": 200.0, "alert_type": "warning"}
    ]

    _save(transactions, budget_rules)
    print("Standard test data generated.")


def generate_random_data(n=30):
    """
    Generate n random transactions over the past 30 days with varying
    dates, amounts, and categories. Useful for stress-testing summaries
    and alert functions with unpredictable inputs.

    Args:
        n (int): Number of transactions to generate (default 30).
    """
    transactions = []
    for _ in range(n):
        category = random.choice(CATEGORIES)
        description = random.choice(DESCRIPTIONS[category])
        amount = round(random.uniform(5.0, 300.0), 2)  # Random amount between 5 and 300
        days_ago = random.randint(0, 29)  # Random day within the last 30 days
        transactions.append({
            "date": make_date(days_ago),
            "amount": amount,
            "category": category,
            "description": description,
            "note": ""
        })

    # Standard budget rules for random data testing
    budget_rules = [
        {"category": "food", "period": "daily", "threshold": 50.0, "alert_type": "warning"},
        {"category": "transport", "period": "weekly", "threshold": 100.0, "alert_type": "warning"},
        {"category": "shopping", "period": "monthly", "threshold": 200.0, "alert_type": "warning"},
        {"category": "entertainment", "period": "weekly", "threshold": 200.0, "alert_type": "warning"}
    ]

    _save(transactions, budget_rules)
    print(f"Random test data generated ({n} transactions).")


def generate_edge_case_empty():
    """
    Edge case: zero transactions.
    Tests that all functions handle empty input without crashing.
    """
    _save([], [])
    print("Edge case generated: empty transactions.")


def generate_edge_case_all_uncategorized():
    """
    Edge case: all transactions have category 'other'.
    Tests that the uncategorized alert fires for every transaction,
    and that budget/percentage alerts do not incorrectly trigger.
    """
    transactions = [
        {"date": make_date(i), "amount": round(random.uniform(10.0, 100.0), 2),
         "category": "other", "description": "Unknown payment", "note": ""}
        for i in range(7)  # 7 days of uncategorized transactions
    ]
    budget_rules = [
        {"category": "food", "period": "daily", "threshold": 50.0, "alert_type": "warning"}
    ]
    _save(transactions, budget_rules)
    print("Edge case generated: all uncategorized transactions.")


def generate_edge_case_zero_amounts():
    """
    Edge case: all transaction amounts are 0.
    Tests that percentage calculation avoids division by zero,
    and that no budget alerts fire on zero spending.
    """
    transactions = [
        {"date": make_date(i), "amount": 0.0, "category": "food",
         "description": "Free meal", "note": "zero amount"}
        for i in range(5)
    ]
    budget_rules = [
        {"category": "food", "period": "daily", "threshold": 50.0, "alert_type": "warning"}
    ]
    _save(transactions, budget_rules)
    print("Edge case generated: all zero-amount transactions.")


def generate_edge_case_single():
    """
    Edge case: only one transaction.
    Tests that single-entry inputs do not cause index errors or
    incorrect consecutive-overspend detection.
    """
    transactions = [
        {"date": make_date(0), "amount": 999.0, "category": "shopping",
         "description": "Big purchase", "note": "single transaction"}
    ]
    budget_rules = [
        {"category": "shopping", "period": "monthly", "threshold": 200.0, "alert_type": "exceed"}
    ]
    _save(transactions, budget_rules)
    print("Edge case generated: single transaction.")


def _save(transactions, budget_rules):
    """
    Internal helper function to save transactions and budget rules to JSON files.

    Args:
        transactions (list): List of transaction dictionaries
        budget_rules (list): List of budget rule dictionaries
    """
    with open(TRANSACTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(transactions, f, indent=4, ensure_ascii=False)
    with open(BUDGET_FILE, "w", encoding="utf-8") as f:
        json.dump(budget_rules, f, indent=4, ensure_ascii=False)
    print(f"Saved to {TRANSACTIONS_FILE} and {BUDGET_FILE}")


if __name__ == "__main__":
    """
    Command-line interface for test data generation.
    Allows user to choose which type of test data to generate.
    """
    print("Select test data to generate:")
    print("  1. Standard test data (covers all alert types)")
    print("  2. Random test data (30 transactions)")
    print("  3. Edge case: empty transactions")
    print("  4. Edge case: all uncategorized")
    print("  5. Edge case: all zero amounts")
    print("  6. Edge case: single transaction")
    choice = input("Enter choice (1-6): ").strip()
    if choice == "1":
        generate_test_data()
    elif choice == "2":
        generate_random_data(30)
    elif choice == "3":
        generate_edge_case_empty()
    elif choice == "4":
        generate_edge_case_all_uncategorized()
    elif choice == "5":
        generate_edge_case_zero_amounts()
    elif choice == "6":
        generate_edge_case_single()
    else:
        print("Invalid choice.")