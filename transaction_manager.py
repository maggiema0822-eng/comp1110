from random import choice

from transaction import Transaction

transactions = []

def add_transaction():
    date = input("Please input the date (YYYY-MM-DD):").strip()
    category = input("Please input the category:").strip()
    description = input("Please input the description:").strip()

    try:
        amount = float(input("Please input the amount:").strip())
    except ValueError:
        print("The amount is invaild, please try again.")
        return

    note = input("Please input your note(if needed):").strip()

    new_trans = Transaction(
        date=date,
        amount=amount,
        category=category,
        description=description,
        note=note
    )

    transactions.append(new_trans)
    print(f"Transaction added successfully")
    return new_trans

def print_transactions():
    print("1 -> all transactions")
    print("2 -> transactions filtered by date")
    print("3 -> transactions filtered by category")
    choice = input("Please choose(1/2/3): ").strip()
    if choice == "1":
        show_all()
    elif choice == "2":
        show_date()
    elif choice == "3":
        show_category()
    else:
        print("Please choose from 1, 2, or 3")

def show_all():
    if not transactions:
        print("No transactions")
        return

    for trans in transactions:
        print(f"{trans.date:<12}{trans.category:<12}${trans.amount:<10.2f}{trans.description:<20}{trans.note}")


def show_date():
    date = input("Please input the date (YYYY-MM-DD): ").strip()

    fix_date = []
    for trans in transactions:
        if trans.date == date:
            fix_date.append(trans)

    if not fix_date:
        print("No transactions")
        return

    for trans in fix_date:
        print(f"{trans.date:<12}{trans.category:<12}${trans.amount:<10.2f}{trans.description:<20}{trans.note}")


def show_category():
    category = input("Please input the category: ").strip()

    fix_category = []
    for trans in transactions:
        if trans.category == category:
            fix_category.append(trans)

    if not fix_category:
        print("No transactions")
        return

    for trans in fix_category:
        print(f"{trans.date:<12}{trans.category:<12}${trans.amount:<10.2f}{trans.description:<20}{trans.note}")


def print_transactions():
    print("1 -> all transactions")
    print("2 -> transactions filtered by date")
    print("3 -> transactions filtered by category")

    user_choice = input("Please choose (1/2/3): ").strip()

    if user_choice == "1":
        show_all()
    elif user_choice == "2":
        show_date()
    elif user_choice == "3":
        show_category()
    else:
        print("Please choose from 1, 2, or 3")