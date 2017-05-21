from collections import Counter
from math import floor


def get_median(dates):
    sorted_dates = sorted(dates)
    if len(sorted_dates) % 2 == 0:
        middle = int(len(sorted_dates) / 2)
        return (sorted_dates[middle] + sorted_dates[middle - 1]) / 2
    else:
        middle = floor(len(sorted_dates) / 2)
        return sorted_dates[middle]


def get_dispersion(dates):
    occurrence = Counter(dates)

    for inc in occurrence:
        occurrence[inc] /= len(dates)

    first = 0   #   M (X ^ 2)
    second = 0  #  [M (X)] ^ 2
    for inc in occurrence:
        first += occurrence[inc] * inc ** 2
        second += occurrence[inc] * inc
    return first - second ** 2
