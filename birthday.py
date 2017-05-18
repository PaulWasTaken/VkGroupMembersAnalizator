import datetime


class Birthday:
    def __init__(self, str_date):
        date = list(map(int, str_date.split(".")))
        if len(date) != 3:
            raise AttributeError
        self.day, self.month, self.year = date

    def get_total_age(self):
        now = datetime.datetime.now()
        if self.month < now.month:
            return now.year - self.year
        else:
            return now.year - self.year - 1

    def get_age_with_month(self):
        age = self.get_total_age()
        now = datetime.datetime.now()
        if self.month < now.month:
            months = 12 + self.month - now.month
        else:
            months = self.month - now.month
        return age + months / 10
