from storage import (
    load_all_transactions,
    save_all_transactions,
    load_budget_rules,
    configure_budget
)

import transaction_manager
from spending_summary import get_summary, format_summary
from alerts import check_all_budget, format_alerts


def main():
    # Load data from storage
    transactions = load_all_transactions()
    rules = load_budget_rules()

    transaction_manager.transactions = transactions

    # Main program loop
    while True:
        print("\n===== Personal Budget Assistant =====")
        print("1. Add transaction")
        print("2. View transactions")
        print("3. Show spending summary")
        print("4. Show budget alerts")
        print("5. Configure budget rule")
        print("6. Save transactions")
        print("0. Exit")

        # Get user input
        choice = input("Please choose: ").strip()

        # Handle menu selection
        if choice == "1":
            transaction_manager.add_transaction()

        elif choice == "2":
            transaction_manager.print_transactions()

        elif choice == "3":
            stats = get_summary(transactions)
            print(format_summary(stats))

        elif choice == "4":
            alerts = check_all_budget(transactions, rules)
            print(format_alerts(alerts))

        elif choice == "5":
            rules = configure_budget()

        elif choice == "6":
            save_all_transactions(transactions)

        elif choice == "0":
            save_all_transactions(transactions)
            print("Data saved. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")


# Run the program
if __name__ == "__main__":
    main()
