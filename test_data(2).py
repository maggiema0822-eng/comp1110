import json
from datetime import datetime, timedelta

TRANSACTIONS_FILE = "transactions.json"
BUDGET_FILE = "budget_rules.json"


def make_date(days_ago):
    return (datetime.now().date() - timedelta(days=days_ago)).strftime("%Y-%m-%d")


def generate_test_data():
    transactions = [
        # normal spending
        {
            "date": make_date(6),
            "amount": 35.0,
            "category": "food",
            "description": "lunch",
            "note": "normal meal"
        },
        {
            "date": make_date(6),
            "amount": 12.0,
            "category": "transport",
            "description": "MTR",
            "note": ""
        },

        # daily food overspend
        {
            "date": make_date(5),
            "amount": 30.0,
            "category": "food",
            "description": "breakfast",
            "note": ""
        },
        {
            "date": make_date(5),
            "amount": 35.0,
            "category": "food",
            "description": "dinner",
            "note": "daily food over budget"
        },

        # consecutive overspend
        {
            "date": make_date(4),
            "amount": 60.0,
            "category": "food",
            "description": "lunch",
            "note": "first overspend day"
        },
        {
            "date": make_date(3),
            "amount": 70.0,
            "category": "food",
            "description": "dinner",
            "note": "second overspend day"
        },

        # percentage alert
        {
            "date": make_date(2),
            "amount": 180.0,
            "category": "transport",
            "description": "taxi",
            "note": "large transport spending"
        },

        # monthly shopping alert
        {
            "date": make_date(1),
            "amount": 260.0,
            "category": "shopping",
            "description": "clothes",
            "note": "monthly shopping over budget"
        },

        # uncategorized alert
        {
            "date": make_date(0),
            "amount": 25.0,
            "category": "other",
            "description": "unknown payment",
            "note": "uncategorized"
        }
    ]

    budget_rules = [
        {
            "category": "food",
            "period": "daily",
            "threshold": 50.0,
            "alert_type": "warning"
        },
        {
            "category": "transport",
            "period": "weekly",
            "threshold": 100.0,
            "alert_type": "warning"
        },
        {
            "category": "shopping",
            "period": "monthly",
            "threshold": 200.0,
            "alert_type": "warning"
        }
    ]

    with open(TRANSACTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(transactions, f, indent=4, ensure_ascii=False)

    with open(BUDGET_FILE, "w", encoding="utf-8") as f:
        json.dump(budget_rules, f, indent=4, ensure_ascii=False)

    print("Test data generated successfully.")
    print("Generated transactions.json")
    print("Generated budget_rules.json")


if __name__ == "__main__":
    generate_test_data()