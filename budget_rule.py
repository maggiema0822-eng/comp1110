class BudgetRule:
    PERIOD_DAYS = {
        "daily": 1,
        "weekly": 7,
        "monthly": 30
    }
    def __init__(self, category, period, threshold, alert_type="warning"):
        self.category = category
        self.period = period
        self.threshold = float(threshold)
        self.alert_type = alert_type
    def get_period_days(self):
        return self.PERIOD_DAYS.get(self.period, 1)
    def to_dict(self):
        return {
            "category": self.category,
            "period": self.period,
            "threshold": self.threshold,
            "alert_type": self.alert_type
        }
    def __str__(self):
        return f"{self.category} | {self.period} | ${self.threshold:.2f} | {self.alert_type}"