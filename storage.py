import json
from datetime import datetime
from transaction import Transaction
from budget_rule import BudgetRule

# File paths for persistent storage
TRANSACTIONS_FILE = "transactions.json"
BUDGET_FILE = "budget_rules.json"


def validate_date(date_string: str) -> bool:
    """
    Validate if a string is in a recognized date format.

    Supported formats:
        - YYYY-MM-DD
        - YYYY/MM/DD
        - DD-MM-YYYY
        - DD/MM/YYYY

    Args:
        date_string (str): The date string to validate

    Returns:
        bool: True if the date format is valid, False otherwise
    """
    try:
        for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y"]:
            try:
                datetime.strptime(date_string, fmt)
                return True
            except ValueError:
                continue
        return False
    except:
        return False


def validate_positive(value: float) -> bool:
    """
    Validate that a numeric value is positive.

    Args:
        value (float): The value to validate

    Returns:
        bool: True if value > 0, False otherwise
    """
    return value > 0


def save_all_transactions(transactions: list[Transaction]) -> None:
    """
    Save all transactions to a JSON file.

    Args:
        transactions (list[Transaction]): List of Transaction objects to save
    """
    try:
        # Convert Transaction objects to dictionaries for JSON serialization
        data = [t.to_dict() for t in transactions]
        with open(TRANSACTIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("Transaction saved successfully")
    except Exception as e:
        print(f"Transaction saved failed: {e}")


def load_all_transactions() -> list[Transaction]:
    """
    Load all transactions from the JSON file.

    Performs validation on date format and positive amounts.
    Invalid transactions are skipped with warning messages.

    Returns:
        list[Transaction]: List of valid Transaction objects, empty list if file not found
    """
    try:
        with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        transactions = []
        for item in data:
            # Validate date format
            if not validate_date(item["date"]):
                print(f"Warning: Invalid date format '{item['date']}', skipping this transaction")
                continue

            # Validate positive amount
            if not validate_positive(item["amount"]):
                print(f"Warning: Negative amount '{item['amount']}' found, skipping this transaction")
                continue

            t = Transaction(
                date=item["date"],
                amount=item["amount"],
                category=item["category"],
                description=item["description"],
                note=item.get("note", "")
            )
            transactions.append(t)
        return transactions
    except FileNotFoundError:
        return []  # Return empty list if file doesn't exist yet
    except Exception as e:
        print(f"Transaction loaded failed: {e}")
        return []


def save_budget_rules(rules: list[BudgetRule]) -> None:
    """
    Save budget rules to a JSON file.

    Args:
        rules (list[BudgetRule]): List of BudgetRule objects to save
    """
    try:
        # Convert BudgetRule objects to dictionaries for JSON serialization
        data = [rule.to_dict() for rule in rules]
        with open(BUDGET_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("Budget rule saved successfully")
    except Exception as e:
        print(f"Budget rule saved failed: {e}")


def load_budget_rules() -> list[BudgetRule]:
    """
    Load budget rules from the JSON file.

    Performs validation on threshold amounts.
    Invalid rules are skipped with warning messages.

    Returns:
        list[BudgetRule]: List of valid BudgetRule objects, empty list if file not found
    """
    try:
        with open(BUDGET_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        rules = []
        for item in data:
            category = item.get("category")
            period = item.get("period")
            threshold = item.get("threshold", 0)
            alert_type = item.get("alert_type", "warning")

            # Validate positive threshold
            if not validate_positive(threshold):
                print(f"Warning: Invalid threshold '{threshold}' for category '{category}', skipping this rule")
                continue

            rule = BudgetRule(category, period, threshold, alert_type)
            rules.append(rule)
        return rules
    except FileNotFoundError:
        return []  # Return empty list if file doesn't exist yet
    except Exception as e:
        print(f"Budget rule loaded failed: {e}")
        return []


def configure_budget() -> list[BudgetRule]:
    """
    Interactive function to configure and add a new budget rule.

    Prompts user for category, period, and threshold amount,
    validates the input, and saves the new rule.

    Returns:
        list[BudgetRule]: Updated list of budget rules
    """
    print("\n===== Configurate Budget rule =====")
    rules = load_budget_rules()

    try:
        cat = input("Input category (such food/cloth)：").strip()
        per = input("Input period (daily/weekly/monthly)：").strip()
        thr = float(input("Input threshold amount："))

        # Validate threshold is positive
        if not validate_positive(thr):
            print("Error: Threshold amount must be positive!")
            return rules

        new_rule = BudgetRule(cat, per, thr)
        rules.append(new_rule)

        save_budget_rules(rules)
        print(f"Rules have been added：{new_rule}")
    except ValueError:
        print("Incorrect input format")

    return rules