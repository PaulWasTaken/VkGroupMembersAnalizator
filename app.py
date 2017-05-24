import argparse

from birthday import Birthday
from formatter import ParseError
from methods.methods import get_median, get_dispersion
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
        self.worker = VkWorker(self.id, self.protected_key, self.group,
                               self.api_version)
        self.precision = settings.precision

        self.median = None
        self.dispersion = None

    def run(self):
        try:
            self.worker.get_access_token(self.port)
            self.get_results()
            print("\nMedian: {}; Dispersion: {}."
                  .format(self.median, self.dispersion))
        except ParseError:
            print("Something wrong with server response. "
                  "It was printed in logs.")
            return
        except timeout:
            print("Server has not responded.")
            return
        except KeyboardInterrupt:
            print("\nInterrupted.")
            return

    def get_results(self):
        dates = []
        for member in self.worker.get_group_members():
            try:
                if self.precision:
                    dates.append(
                        Birthday(member["bdate"]).get_age_with_month())
                else:
                    dates.append(Birthday(member["bdate"]).get_total_age())
            except AttributeError:
                continue  # A person turned off showing his birth year.
            except KeyError:
                continue  # A person hide his birth date.
        self.median, self.dispersion = get_median(dates), get_dispersion(dates)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("group", metavar="group",
                   help="Set the group name you want to be analyzed.")
    p.add_argument("-p", dest="precision", action="store_true",
                   help="Enable calculating with months.")
    Application(p.parse_args()).run()
