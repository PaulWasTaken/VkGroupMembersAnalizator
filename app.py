from birthday import Birthday
from math import floor
from server_worker import VkWorker
from socket import timeout


def get_median_and_dispersion(dates):
    sorted_dates = sorted(dates)
    if len(sorted_dates) % 2 == 0:
        middle = len(sorted_dates) / 2
        median = (sorted_dates[middle] + sorted_dates[middle - 1]) / 2
    else:
        middle = floor(len(sorted_dates) / 2)
        median = sorted_dates[middle]

    occurrence = {}
    for date in sorted_dates:
        if date not in occurrence:
            occurrence[date] = 0
        occurrence[date] += 1

    for inc in occurrence:
        occurrence[inc] /= len(sorted_dates)

    first = 0   #   M (X ^ 2)
    second = 0  #  [M (X)] ^ 2
    for inc in occurrence:
        first += occurrence[inc] * inc ** 2
        second += occurrence[inc] * inc
    dispersion = first - second ** 2
    return median, dispersion


class Application:
    def __init__(self):
        self.id = 6020893
        self.protected_key = "1JqRjnPQVVQJyUx7O6UN"
        self.service_key = '8cf6ae288cf6ae288cf6ae28028cad71358' \
                           '8cf68cf6ae28d5f99d9e5ce04f9e42d8f4f1'
        self.port = 64325
        self.api_version = 5.64  # Get it from https://vk.com/dev/implicit_flow_user
        self.worker = VkWorker()
        self.token = None
        self.time_left = None
        self.user_id = None
        self.median = None
        self.dispersion = None

    def run(self):
        try:
            self.get_access_token()
        except (timeout, ConnectionError):
            print("Server has not responded.")
            return
        self.get_results()
        print("Median: {}; Dispersion: {}."
              .format(self.median, self.dispersion))

    def get_results(self):
        dates = []
        for member in self.worker.get_group_members(
                "kn1012015", self.token, self.api_version):
            try:
                dates.append(Birthday(member["bdate"]).get_total_age())
            except AttributeError:
                continue    # A person turned off showing his birth year.
            except KeyError:
                continue    # A person hide his birth date.
        self.median, self.dispersion = get_median_and_dispersion(dates)

    def get_access_token(self):
        self.token, self.time_left, self.user_id = \
            self.worker.get_access_token(
                self.id, self.port, self.api_version, self.protected_key)


if __name__ == "__main__":
    Application().run()
