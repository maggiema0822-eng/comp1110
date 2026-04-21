import json
from datetime import datetime
from transaction import Transaction
from budget_rule import BudgetRule

TRANSACTIONS_FILE = "transactions.json"
BUDGET_FILE = "budget_rules.json"


def validate_date(date_string: str) -> bool:
    """验证日期格式是否正确"""
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
    """验证数值是否为正数"""
    return value > 0


def save_all_transactions(transactions: list[Transaction]) -> None:
    try:
        data = [t.to_dict() for t in transactions]
        with open(TRANSACTIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("Transaction saved successfully")
    except Exception as e:
        print(f"Transaction saved failed: {e}")


def load_all_transactions() -> list[Transaction]:
    try:
        with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        transactions = []
        for item in data:
            if not validate_date(item["date"]):
                print(f"Warning: Invalid date format '{item['date']}', skipping this transaction")
                continue
            
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
        return []
    except Exception as e:
        print(f"Transaction loaded failed: {e}")
        return []


def save_budget_rules(rules: list[BudgetRule]) -> None:
    try:
        data = [rule.to_dict() for rule in rules]
        with open(BUDGET_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("Budget rule saved successfully")
    except Exception as e:
        print(f"Budget rule saved failed: {e}")


def load_budget_rules() -> list[BudgetRule]:
    try:
        with open(BUDGET_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        rules = []
        for item in data:
            category = item.get("category")
            period = item.get("period")
            threshold = item.get("threshold", 0)
            alert_type = item.get("alert_type", "warning")
            
            if not validate_positive(threshold):
                print(f"Warning: Invalid threshold '{threshold}' for category '{category}', skipping this rule")
                continue

            rule = BudgetRule(category, period, threshold, alert_type)
            rules.append(rule)
        return rules
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Budget rule loaded failed: {e}")
        return []


def configure_budget() -> list[BudgetRule]:
    print("\n===== Configurate Budget rule =====")
    rules = load_budget_rules()

    try:
        cat = input("Input category (such food/cloth)：").strip()
        per = input("Input period (daily/weekly/monthly)：").strip()
        thr = float(input("Input threshold amount："))

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