from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from transaction import Transaction


def calculating_total_spending(tran: List[Transaction]) -> float:
    """
    Calculate the total amount spent across all transactions.

    Args:
        tran: List of Transaction objects.

    Returns:
        Sum of all transaction amounts as a float.
    """
    return sum(t.amount for t in tran)


def calculate_by_category(tran: List[Transaction]) -> Dict[str, float]:
    """
    Aggregate total spending grouped by category.

    Args:
        tran: List of Transaction objects.

    Returns:
        Dict mapping each category name to its total spending amount.
    """
    total = {}
    for t in tran:
        if t.category not in total:
            total[t.category] = t.amount
        else:
            total[t.category] += t.amount
    return total


def calculate_by_day(tran: List[Transaction]) -> Dict[str, float]:
    """
    Aggregate total spending grouped by day.

    Args:
        tran: List of Transaction objects.

    Returns:
        Dict mapping each date string ("YYYY-MM-DD") to its total spending amount.
    """
    total = {}
    for t in tran:
        if t.date not in total:
            total[t.date] = t.amount
        else:
            total[t.date] += t.amount
    return total


def calculate_by_week(tran: List[Transaction]) -> Dict[str, float]:
    """
    Aggregate total spending grouped by calendar week.

    Each week is identified by its Monday date. Transactions are mapped to
    the Monday of their respective week and totalled.

    Args:
        tran: List of Transaction objects.

    Returns:
        Dict mapping each week-start date string ("YYYY-MM-DD") to its total
        spending amount.
    """
    total = {}
    for t in tran:
        date = datetime.strptime(t.date, "%Y-%m-%d")
        start = date - timedelta(days=date.weekday())
        key = start.strftime("%Y-%m-%d")
        if key in total:
            total[key] += t.amount
        else:
            total[key] = t.amount
    return total


def calculate_by_month(tran: List[Transaction]) -> Dict[str, float]:
    """
    Aggregate total spending grouped by calendar month.

    Each month is identified by its "YYYY-MM" prefix.

    Args:
        tran: List of Transaction objects.

    Returns:
        Dict mapping each month string ("YYYY-MM") to its total spending amount.
    """
    total = {}
    for t in tran:
        key = t.date[:7]
        if key in total:
            total[key] += t.amount
        else:
            total[key] = t.amount
    return total


def get_top_categories(tran: List[Transaction], topn: int = 3) -> List[Tuple[str, float]]:
    """
    Return the top N categories by total spending, in descending order.

    Uses a bubble sort to rank categories without relying on built-in sort.

    Args:
        tran: List of Transaction objects.
        topn: Number of top categories to return (default 3).

    Returns:
        List of (category, total_amount) tuples, sorted from highest to lowest
        spending, capped at topn entries.
    """
    totals = calculate_by_category(tran)
    list_n = []
    for k, v in totals.items():
        list_n.append((k, v))
    for i in range(len(list_n)):
        for j in range(i + 1, len(list_n)):
            if list_n[i][1] < list_n[j][1]:
                list_n[i], list_n[j] = list_n[j], list_n[i]
    return list_n[:topn]


def calculate_spending_trend(tran: List[Transaction], days: int = 7) -> Dict:
    """
    Compute spending trend statistics for the most recent N days compared to
    the preceding N-day period.

    The current period covers [today - (days-1), today]. The previous period
    covers the N days immediately before that. The percentage change between
    the two periods is included if previous spending is non-zero.

    Args:
        tran: List of Transaction objects.
        days: Number of days to include in the trend window (default 7).

    Returns:
        Dict with the following keys:
            - "days": the window size
            - "total": total spending in the current period
            - "daily_avg": average spending per day in the current period
            - "by_day": dict of date -> amount for days with spending
            - "days_with_spending": number of distinct days with spending
            - "previous_total": total spending in the preceding period
            - "previous_change_pct": percentage change vs previous period,
              or None if previous total was zero but current is non-zero
    """
    today = datetime.now().date()
    start = today - timedelta(days=days - 1)

    period = []
    for t in tran:
        t_date = datetime.strptime(t.date, "%Y-%m-%d").date()
        if start <= t_date <= today:
            period.append(t)

    spend = {}
    total = 0.0
    for t in period:
        spend[t.date] = spend.get(t.date, 0.0) + t.amount
        total += t.amount

    daily_avg = total / days if days > 0 else 0.0
    days_with_spending = len(spend)

    prev_end = start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=days - 1)

    prev_total = 0.0
    for t in tran:
        t_date = datetime.strptime(t.date, "%Y-%m-%d").date()
        if prev_start <= t_date <= prev_end:
            prev_total += t.amount

    if prev_total > 0:
        change_pct = (total - prev_total) / prev_total * 100
    else:
        change_pct = None if total > 0 else 0.0

    return {
        "days": days,
        "total": total,
        "daily_avg": daily_avg,
        "by_day": dict(sorted(spend.items())),
        "days_with_spending": days_with_spending,
        "previous_total": prev_total,
        "previous_change_pct": change_pct
    }


def get_summary(tran: List[Transaction]) -> Dict:
    """
    Generate a complete spending summary report for a list of transactions.

    Computes total spending, breakdowns by category/day/week/month, the top 3
    categories, and spending trends for the last 7 and 30 days. Returns a
    zeroed-out structure if the transaction list is empty.

    Args:
        tran: List of Transaction objects.

    Returns:
        Dict with keys:
            - "total_spending": float
            - "by_category": Dict[str, float]
            - "by_day": Dict[str, float]
            - "by_week": Dict[str, float]
            - "by_month": Dict[str, float]
            - "top_categories": List[Tuple[str, float]]
            - "trend_7days": Dict (from calculate_spending_trend)
            - "trend_30days": Dict (from calculate_spending_trend)
    """
    if not tran:
        return {
            "total_spending": 0.0,
            "by_category": {},
            "by_day": {},
            "by_week": {},
            "by_month": {},
            "top_categories": [],
            "trend_7days": calculate_spending_trend(tran, 7),
            "trend_30days": calculate_spending_trend(tran, 30),
        }
    total = calculating_total_spending(tran)
    by_category = calculate_by_category(tran)
    by_day = calculate_by_day(tran)
    by_week = calculate_by_week(tran)
    by_month = calculate_by_month(tran)
    top_categories = get_top_categories(tran, 3)
    trend_7days = calculate_spending_trend(tran, 7)
    trend_30days = calculate_spending_trend(tran, 30)
    return {
        "total_spending": total,
        "by_category": by_category,
        "by_day": by_day,
        "by_week": by_week,
        "by_month": by_month,
        "top_categories": top_categories,
        "trend_7days": trend_7days,
        "trend_30days": trend_30days,
    }


def format_summary(stats: Dict) -> str:
    """
    Format a spending summary dict into a human-readable report string.

    Displays sections for total spending, per-category breakdown, top 3
    categories, daily spending for the last 7 days, weekly spending (up to
    5 most recent weeks), monthly spending, and 7-day / 30-day trends with
    percentage change vs the preceding period.

    Args:
        stats: Dict returned by get_summary().

    Returns:
        A formatted multi-line string ready to be printed to the console.
        Returns a plain message string if no transactions are present.
    """
    if not stats["by_category"]:
        return "No transactions found. Please add some transactions first."
    lines = []
    lines.append("=" * 60)
    lines.append("SPENDING SUMMARY")
    lines.append("=" * 60)
    lines.append(f"Total spending:        ${stats['total_spending']:.2f}")
    lines.append("")
    lines.append("-" * 60)
    lines.append("SPENDING BY CATEGORY")
    lines.append("-" * 60)
    sorted_cat = []
    for category, amount in stats["by_category"].items():
        sorted_cat.append((category, amount))
    for i in range(len(sorted_cat)):
        for j in range(i + 1, len(sorted_cat)):
            if sorted_cat[i][1] < sorted_cat[j][1]:
                sorted_cat[i], sorted_cat[j] = sorted_cat[j], sorted_cat[i]
    for category, amount in sorted_cat:
        percentage = (amount / stats["total_spending"] * 100) if stats["total_spending"] > 0 else 0
        lines.append(f"  {category:15} : ${amount:8.2f}  ({percentage:5.1f}%)")
    lines.append("")
    lines.append("-" * 60)
    lines.append("TOP 3 CATEGORIES")
    lines.append("-" * 60)
    for i, (category, amount) in enumerate(stats["top_categories"], 1):
        percentage = (amount / stats["total_spending"] * 100) if stats["total_spending"] > 0 else 0
        lines.append(f"  {i}. {category:15} : ${amount:8.2f}  ({percentage:.1f}%)")
    lines.append("")
    lines.append("-" * 60)
    lines.append("DAILY SPENDING (Last 7 Days)")
    lines.append("-" * 60)
    today = datetime.now().date()
    last_7day = []
    for i in range(7):
        day = today - timedelta(days=i)
        last_7day.append(day.strftime("%Y-%m-%d"))
    for day in reversed(last_7day):
        amount = stats["by_day"].get(day, 0.0)
        lines.append(f"  {day} : ${amount:.2f}")
    lines.append("")
    lines.append("-" * 60)
    lines.append("WEEKLY SPENDING")
    lines.append("-" * 60)
    weeks = []
    for week in stats["by_week"].keys():
        weeks.append(week)
    for i in range(len(weeks)):
        for j in range(i + 1, len(weeks)):
            if weeks[i] < weeks[j]:
                weeks[i], weeks[j] = weeks[j], weeks[i]
    for week in weeks[:5]:
        lines.append(f"  Week starting {week} : ${stats['by_week'][week]:.2f}")
    if not stats["by_week"]:
        lines.append("No weekly data")
    lines.append("")
    lines.append("-" * 60)
    lines.append("MONTHLY SPENDING")
    lines.append("-" * 60)
    months = []
    for month in stats["by_month"].keys():
        months.append(month)
    for i in range(len(months)):
        for j in range(i + 1, len(months)):
            if months[i] < months[j]:
                months[i], months[j] = months[j], months[i]
    for month in months:
        lines.append(f"  Month {month} : ${stats['by_month'][month]:.2f}")
    if not stats["by_month"]:
        lines.append("No monthly data")
    lines.append("")
    lines.append("-" * 60)
    lines.append("SPENDING TRENDS")
    lines.append("-" * 60)
    trend7 = stats["trend_7days"]
    lines.append("Last 7 days:")
    lines.append(f"  Total: ${trend7['total']:.2f}")
    lines.append(f"  Daily average: ${trend7['daily_avg']:.2f}")
    if trend7["previous_change_pct"] is None:
        lines.append("  Change from previous 7 days: N/A (no previous spending)")
    elif trend7["previous_change_pct"] > 0:
        lines.append(f"  Change from previous 7 days: +{trend7['previous_change_pct']:.1f}% ↑")
    elif trend7["previous_change_pct"] < 0:
        lines.append(f"  Change from previous 7 days: {trend7['previous_change_pct']:.1f}% ↓")
    else:
        lines.append("  Change from previous 7 days: 0.0% (no change)")
    trend30 = stats["trend_30days"]
    lines.append("")
    lines.append("Last 30 days:")
    lines.append(f"  Total: ${trend30['total']:.2f}")
    lines.append(f"  Daily average: ${trend30['daily_avg']:.2f}")
    if trend30["previous_change_pct"] is None:
        lines.append("  Change from previous 30 days: N/A (no previous spending)")
    elif trend30["previous_change_pct"] > 0:
        lines.append(f"  Change from previous 30 days: +{trend30['previous_change_pct']:.1f}% ↑")
    elif trend30["previous_change_pct"] < 0:
        lines.append(f"  Change from previous 30 days: {trend30['previous_change_pct']:.1f}% ↓")
    else:
        lines.append("  Change from previous 30 days: 0.0% (no change)")
    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)
