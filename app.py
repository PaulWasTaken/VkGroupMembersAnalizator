import argparse

from birthday import Birthday
from methods.methods import log_on, get_median, get_dispersion
from server_worker import VkWorker
from socket import timeout


class Application:
    def __init__(self, settings):
        self.id = 6020893
        self.protected_key = "1JqRjnPQVVQJyUx7O6UN"
        self.service_key = '8cf6ae288cf6ae288cf6ae28028cad71358' \
                           '8cf68cf6ae28d5f99d9e5ce04f9e42d8f4f1'
        self.port = 64325
        self.api_version = 5.64  # Get it from https://vk.com/dev/implicit_flow_user
        self.group = settings.group
        self.worker = VkWorker()
        self.token = None
        self.time_left = None
        self.user_id = None
        self.median = None
        self.dispersion = None

        if settings.debug:
            log_on()

    def run(self):
        try:
            self.get_access_token()
        except (timeout, ConnectionError):
            print("Server has not responded.")
            return

        try:
            self.get_results()
            print("\nMedian: {}; Dispersion: {}."
                  .format(self.median, self.dispersion))
        except KeyboardInterrupt:
            print("\nInterrupted.")
            return

    def get_results(self):
        dates = []
        for member in self.worker.get_group_members(
                self.group, self.token, self.api_version):
            try:
                dates.append(Birthday(member["bdate"]).get_total_age())
            except AttributeError:
                continue    # A person turned off showing his birth year.
            except KeyError:
                continue    # A person hide his birth date.
        self.median, self.dispersion = get_median(dates), get_dispersion(dates)

    def get_access_token(self):
        self.token, self.time_left, self.user_id = \
            self.worker.get_access_token(
                self.id, self.port, self.api_version, self.protected_key)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("group", metavar="group",
                   help="Set the group name you want to be analyzed.")
    p.add_argument("-d", dest="debug", action='store_true',
                   help="Enable printing statuses.")
    Application(p.parse_args()).run()
