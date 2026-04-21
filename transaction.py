class Transaction:
    def __init__(self, date, amount, category, description, note=""):
        self.date = date
        self.amount = float(amount)
        self.category = category
        self.description = description
        self.note = note
    def to_dict(self):
        return {
            "date": self.date,
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "note": self.note
        }
    def __str__(self):
        return f"{self.date} | ${self.amount:.2f} | {self.category} | {self.description}"