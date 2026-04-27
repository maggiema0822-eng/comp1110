# COMP1110 — Personal Budget and Spending Assistant
**Topic A | The University of Hong Kong | Semester 2, 2025–2026**

---

## Overview

This project models everyday personal spending as a computing problem. The program allows users to record transactions, define budget rules, view spending summaries, and receive rule-based alerts when spending exceeds defined thresholds.

---

## How to Run

```bash
python main.py
```

The program will load existing data from `transactions.json` and `budget_rules.json` if they exist. If no data files are found, the program will start with empty records.

To generate sample test data before running:

```bash
python test_data.py
```

---

## File Descriptions

| File | Description |
|------|-------------|
| `main.py` | Entry point. Provides a text-based menu for adding transactions, viewing summaries, checking alerts, and managing budget rules. |
| `transaction.py` | Defines the `Transaction` class. Each transaction stores a date, amount, category, description, and optional note. |
| `budget_rule.py` | Defines the `BudgetRule` class. Each rule specifies a category, time period (daily/weekly/monthly), spending threshold, and alert type. |
| `alerts.py` | Implements all rule-based alert checks: daily/weekly/monthly budget caps, percentage threshold, consecutive overspend detection, and uncategorised transaction warnings. |
| `spending_summary.py` | Computes spending statistics including totals by category, daily/weekly/monthly breakdowns, top 3 categories, and 7/30-day spending trends. |
| `storage.py` | Handles loading and saving transactions and budget rules to/from JSON files. Handles missing files, empty files, and malformed data gracefully. |
| `test_data.py` | Generates sample test data for development and testing purposes. Includes a standard test set covering all alert types, random data generation, and multiple edge cases. |

---

## Data Folder

The `data/` folder contains sample input files for the four case studies used in the Group Final Report.

| File | Description |
|------|-------------|
| `case1_transactions.csv` | Transactions for Case Study 1: daily food budget HK$50 |
| `case1_budget_rules.csv` | Budget rules for Case Study 1 |
| `case2_transactions.csv` | Transactions for Case Study 2: monthly transport tracking |
| `case2_budget_rules.csv` | Budget rules for Case Study 2 |
| `case3_transactions.csv` | Transactions for Case Study 3: subscription creep detection |
| `case3_budget_rules.csv` | Budget rules for Case Study 3 |
| `case4_transactions.csv` | Transactions for Case Study 4: weekly entertainment budget |
| `case4_budget_rules.csv` | Budget rules for Case Study 4 |

---

## Data File Format

**transactions.json**
```json
[
    {
        "date": "2026-03-01",
        "amount": 35.0,
        "category": "food",
        "description": "Canteen lunch",
        "note": ""
    }
]
```

**budget_rules.json**
```json
[
    {
        "category": "food",
        "period": "daily",
        "threshold": 50.0,
        "alert_type": "warning"
    }
]
```

Valid values:
- `period`: `daily`, `weekly`, `monthly`
- `alert_type`: `warning`, `exceed`
- `category`: `food`, `transport`, `shopping`, `entertainment`, `subscription`, `other`

---

## Test Cases

Run `test_data.py` and select from the following options:

| Option | Description |
|--------|-------------|
| 1 | Standard test data — covers all alert types (daily overspend, consecutive overspend, percentage alert, monthly budget, uncategorised) |
| 2 | Random test data — 30 randomly generated transactions for stress testing |
| 3 | Edge case: empty transaction list |
| 4 | Edge case: all transactions uncategorised |
| 5 | Edge case: all transaction amounts are zero |
| 6 | Edge case: single transaction only |

---

## GitHub Repository

[https://github.com/maggiema0822-eng/comp1110](https://github.com/maggiema0822-eng/comp1110)
