class Expense:
    def __init__(self, category, amount, date):
        self.category = category
        self.amount = amount
        self.date = date

    def __str__(self):
        return f"{self.date} | {self.category} | {self.amount}円"