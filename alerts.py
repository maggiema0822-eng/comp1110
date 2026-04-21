from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from transaction import Transaction
from budget_rule import BudgetRule


def get_transactions_in_range(tran: List[Transaction], start_date: str, end_date: str) -> List[Transaction]:
    """
    Filter transactions within a given date range (inclusive).

    Args:
        tran: List of Transaction objects to filter.
        start_date: Start date string in "YYYY-MM-DD" format.
        end_date: End date string in "YYYY-MM-DD" format.

    Returns:
        List of Transaction objects whose date falls within [start_date, end_date].
    """
    result = []
    for t in tran:
        if start_date <= t.date <= end_date:
            result.append(t)
    return result


def check_daily_budget(tran: List[Transaction], rule: BudgetRule) -> List[Tuple[str, float, float, str]]:
    """
    Check whether daily spending in a given category exceeds the budget rule threshold.

    For each day that has transactions matching the rule's category, the total
    spending is accumulated. If it exceeds rule.threshold, an alert is generated.

    Args:
        tran: List of Transaction objects.
        rule: BudgetRule specifying the category, threshold, and alert type.

    Returns:
        Sorted list of tuples (date, total_spent, threshold, alert_type),
        one entry per day where spending exceeded the threshold.
    """
    daily_spend = {}
    for t in tran:
        if t.category == rule.category:
            if t.date in daily_spend:
                daily_spend[t.date] += t.amount
            else:
                daily_spend[t.date] = t.amount
    alerts = []
    for date, spend in daily_spend.items():
        if spend > rule.threshold:
            alert_type = "WARNING" if rule.alert_type == "warning" else "EXCEED"
            alerts.append((date, spend, rule.threshold, alert_type))
    return sorted(alerts, key=lambda x: x[0])


def check_weekly_budget(tran: List[Transaction], rule: BudgetRule) -> List[Tuple[str, float, float, str]]:
    """
    Check whether weekly spending in a given category exceeds the budget rule threshold.

    Weeks are anchored to Monday. Each transaction is mapped to the Monday of its
    week, and spending is accumulated per week. If the weekly total exceeds
    rule.threshold, an alert is generated.

    Args:
        tran: List of Transaction objects.
        rule: BudgetRule specifying the category, threshold, and alert type.

    Returns:
        Sorted list of tuples (week_start_date, total_spent, threshold, alert_type),
        one entry per week where spending exceeded the threshold.
    """
    weekly_spend = {}
    for t in tran:
        if t.category == rule.category:
            date = datetime.strptime(t.date, "%Y-%m-%d").date()
            start = date - timedelta(days=date.weekday())
            key = start.strftime("%Y-%m-%d")
            if key in weekly_spend:
                weekly_spend[key] += t.amount
            else:
                weekly_spend[key] = t.amount
    alerts = []
    for week, spend in weekly_spend.items():
        if spend > rule.threshold:
            alert_type = "WARNING" if rule.alert_type == "warning" else "EXCEED"
            alerts.append((week, spend, rule.threshold, alert_type))
    return sorted(alerts, key=lambda x: x[0])


def check_monthly_budget(tran: List[Transaction], rule: BudgetRule) -> List[Tuple[str, float, float, str]]:
    """
    Check whether monthly spending in a given category exceeds the budget rule threshold.

    Months are identified by the "YYYY-MM" prefix of the transaction date. Spending
    is accumulated per month. If the monthly total exceeds rule.threshold, an alert
    is generated.

    Args:
        tran: List of Transaction objects.
        rule: BudgetRule specifying the category, threshold, and alert type.

    Returns:
        Sorted list of tuples (month, total_spent, threshold, alert_type),
        one entry per month where spending exceeded the threshold.
    """
    monthly_spend = {}
    for t in tran:
        if t.category == rule.category:
            key = t.date[:7]
            if key in monthly_spend:
                monthly_spend[key] += t.amount
            else:
                monthly_spend[key] = t.amount
    alerts = []
    for month, spend in monthly_spend.items():
        if spend > rule.threshold:
            alert_type = "WARNING" if rule.alert_type == "warning" else "EXCEED"
            alerts.append((month, spend, rule.threshold, alert_type))
    return sorted(alerts, key=lambda x: x[0])


def check_percentage(tran: List[Transaction], threshold: float = 30.0) -> List[Tuple[str, float, float]]:
    """
    Identify spending categories that exceed a given percentage of total spending.

    Computes each category's share of total spending. Any category whose share
    exceeds the threshold is included in the result, sorted in descending order
    of percentage.

    Args:
        tran: List of Transaction objects.
        threshold: Percentage threshold (default 30.0). Categories above this
                   percentage of total spending will trigger an alert.

    Returns:
        List of tuples (category, percentage, amount), sorted from highest to
        lowest percentage. Empty list if total spending is zero.
    """
    total = 0.0
    for t in tran:
        total += t.amount
    if total == 0:
        return []
    category = {}
    for t in tran:
        if t.category in category:
            category[t.category] += t.amount
        else:
            category[t.category] = t.amount
    alerts = []
    for category, amount in category.items():
        percentage = (amount / total) * 100
        if percentage > threshold:
            alerts.append((category, percentage, amount))
    for i in range(len(alerts)):
        for j in range(i + 1, len(alerts)):
            if alerts[i][1] < alerts[j][1]:
                alerts[i], alerts[j] = alerts[j], alerts[i]
    return alerts


def check_consecutive_overspend(tran: List[Transaction], rule: BudgetRule, consecutive_days: int = 2) -> List[Tuple[str, int, float, float]]:
    """
    Detect streaks of consecutive days where daily spending exceeds the budget threshold.

    For each day with qualifying transactions, daily totals are computed. Days that
    exceed rule.threshold are identified, then grouped into consecutive streaks. Only
    streaks of length >= consecutive_days are reported.

    Args:
        tran: List of Transaction objects.
        rule: BudgetRule specifying the category and threshold.
        consecutive_days: Minimum number of consecutive overspend days to trigger
                          an alert (default 2).

    Returns:
        List of tuples (streak_start_date, streak_length, avg_excess, threshold),
        one entry per qualifying streak.
    """
    daily_spend = {}
    for t in tran:
        if t.category == rule.category:
            if t.date in daily_spend:
                daily_spend[t.date] += t.amount
            else:
                daily_spend[t.date] = t.amount

    overspend_dates = []
    for date, amount in daily_spend.items():
        if amount > rule.threshold:
            overspend_dates.append(date)

    overspend_dates.sort()
    alerts = []

    if not overspend_dates:
        return alerts

    streak = [overspend_dates[0]]

    for i in range(1, len(overspend_dates)):
        prev_date = datetime.strptime(overspend_dates[i - 1], "%Y-%m-%d").date()
        curr_date = datetime.strptime(overspend_dates[i], "%Y-%m-%d").date()

        if curr_date == prev_date + timedelta(days=1):
            streak.append(overspend_dates[i])
        else:
            if len(streak) >= consecutive_days:
                total_excess = 0.0
                for d in streak:
                    total_excess += daily_spend[d] - rule.threshold
                avg_excess = total_excess / len(streak)
                alerts.append((streak[0], len(streak), avg_excess, rule.threshold))
            streak = [overspend_dates[i]]

    if len(streak) >= consecutive_days:
        total_excess = 0.0
        for d in streak:
            total_excess += daily_spend[d] - rule.threshold
        avg_excess = total_excess / len(streak)
        alerts.append((streak[0], len(streak), avg_excess, rule.threshold))

    return alerts


def check_uncategorized(tran: List[Transaction]) -> List[Dict]:
    """
    Find transactions that are uncategorized or have a generic "other" category.

    A transaction is considered uncategorized if its category is "other",
    an empty string, or None.

    Args:
        tran: List of Transaction objects.

    Returns:
        List of dicts, each containing "date", "amount", "description", and
        "category" for each uncategorized transaction.
    """
    uncategorized = []
    for t in tran:
        if t.category == "other" or t.category == "" or t.category is None:
            uncategorized.append({
                "date": t.date,
                "amount": t.amount,
                "description": t.description,
                "category": t.category,
            })
    return uncategorized


def check_all_budget(tran: List[Transaction], rules: List[BudgetRule]) -> Dict:
    """
    Run all budget alert checks and aggregate results into a single report.

    Iterates over each BudgetRule and applies the appropriate period check
    (daily, weekly, or monthly). Also runs percentage threshold, consecutive
    overspend, and uncategorized transaction checks across all transactions.

    Args:
        tran: List of Transaction objects.
        rules: List of BudgetRule objects defining budget constraints.

    Returns:
        Dict with four keys:
            - "budget_alerts": list of dicts for period-based threshold violations
            - "percentage_alerts": list of dicts for category percentage violations
            - "consecutive_overspend": list of dicts for consecutive overspend streaks
            - "uncategorized": list of dicts for uncategorized transactions
    """
    alerts = {
        "budget_alerts": [],
        "percentage_alerts": [],
        "consecutive_overspend": [],
        "uncategorized": [],
    }
    for rule in rules:
        if rule.period == "daily":
            daily_alerts = check_daily_budget(tran, rule)
            for date, spent, threshold, alert_type in daily_alerts:
                alerts["budget_alerts"].append({
                    "type": alert_type,
                    "category": rule.category,
                    "period": "daily",
                    "date": date,
                    "spent": spent,
                    "threshold": threshold,
                    "message": f"[{alert_type}] {rule.category} on {date}: ${spent:.2f} > ${threshold:.2f}"
                })
        elif rule.period == "weekly":
            weekly_alerts = check_weekly_budget(tran, rule)
            for week, spent, threshold, alert_type in weekly_alerts:
                alerts["budget_alerts"].append({
                    "type": alert_type,
                    "category": rule.category,
                    "period": "weekly",
                    "week": week,
                    "spent": spent,
                    "threshold": threshold,
                    "message": f"[{alert_type}] {rule.category} week starting {week}: ${spent:.2f} > ${threshold:.2f}"
                })
        elif rule.period == "monthly":
            monthly_alerts = check_monthly_budget(tran, rule)
            for month, spent, threshold, alert_type in monthly_alerts:
                alerts["budget_alerts"].append({
                    "type": alert_type,
                    "category": rule.category,
                    "period": "monthly",
                    "month": month,
                    "spent": spent,
                    "threshold": threshold,
                    "message": f"[{alert_type}] {rule.category} in {month}: ${spent:.2f} > ${threshold:.2f}"
                })
        if rule.period == "daily":
            consecutive = check_consecutive_overspend(tran, rule, 2)
            for start_date, days, avg_excess, threshold in consecutive:
                alerts["consecutive_overspend"].append({
                    "category": rule.category,
                    "start_date": start_date,
                    "consecutive_days": days,
                    "avg_excess": avg_excess,
                    "threshold": threshold,
                    "message": f"[CONSECUTIVE] {rule.category} exceeded budget for {days} consecutive days starting {start_date} (avg excess: ${avg_excess:.2f})"
                })
    percentage_alerts = check_percentage(tran, 30.0)
    for category, percentage, amount in percentage_alerts:
        alerts["percentage_alerts"].append({
            "category": category,
            "percentage": percentage,
            "amount": amount,
            "message": f"[PERCENTAGE] {category} accounts for {percentage:.1f}% (${amount:.2f}) of total spending - exceeds 30% threshold"
        })
    uncategorized = check_uncategorized(tran)
    for t in uncategorized:
        alerts["uncategorized"].append({
            "date": t["date"],
            "amount": t["amount"],
            "description": t["description"],
            "message": f"[UNCATEGORIZED] {t['date']}: ${t['amount']:.2f} - {t['description']}"
        })

    return alerts


def format_alerts(alerts: Dict) -> str:
    """
    Format the aggregated alerts dictionary into a human-readable string.

    Organises alerts into four sections: budget limit alerts, percentage threshold
    alerts, consecutive overspend alerts, and uncategorized transactions. If no
    alerts exist in any section, a "No alerts" message is shown instead.

    Args:
        alerts: Dict returned by check_all_budget(), containing the four alert
                categories.

    Returns:
        A formatted multi-line string ready to be printed to the console.
    """
    lines = []
    lines.append("=" * 60)
    lines.append("BUDGET ALERTS")
    lines.append("=" * 60)
    has_alerts = False
    if alerts["budget_alerts"]:
        has_alerts = True
        lines.append("\n[Budget Limit Alerts]")
        for alert in alerts["budget_alerts"]:
            lines.append(f"  {alert['message']}")
    if alerts["percentage_alerts"]:
        has_alerts = True
        lines.append("\n[Percentage Threshold Alerts]")
        for alert in alerts["percentage_alerts"]:
            lines.append(f"  {alert['message']}")
    if alerts["consecutive_overspend"]:
        has_alerts = True
        lines.append("\n[Consecutive Overspend Alerts]")
        for alert in alerts["consecutive_overspend"]:
            lines.append(f"  {alert['message']}")
    if alerts["uncategorized"]:
        has_alerts = True
        lines.append("\n[Uncategorized Transactions]")
        for alert in alerts["uncategorized"]:
            lines.append(f"  {alert['message']}")
    if not has_alerts:
        lines.append("\n  No alerts! All spending is within budget.")
    lines.append("\n" + "=" * 60)
    return "\n".join(lines)
