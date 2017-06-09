import webbrowser

from _socket import timeout
from collections import Counter
from math import floor
from select import select
from threading import Timer
from time import time
from urllib.request import urlopen


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


def get_url_response(url, kwargs):
    with urlopen(url.format(**kwargs)) as response:
        return response.read().decode()


def receive_data(sock, base_page=None):
    beginning_time = time()
    while time() - beginning_time < 2:
        r, _, _ = select([sock], [], [])
        for s in r:
            if s == sock:
                conn, addr = sock.accept()
                data = conn.recv(4096).decode()
                if base_page:
                    conn.sendto(base_page, addr)
                return data
    raise timeout


def get_base_page(filename):
    base_page = b"HTTP/1.1 200 OK\r\n" \
                b"Content-Type: text/html; " \
                b"charset=utf-8\r\n\r\n"
    try:
        with open(filename, "rb") as reader:
            base_page += reader.read()
    except (IOError, FileExistsError, FileNotFoundError):
        base_page += b"<html><body>Sorry, no base page was " \
                     b"found, but authorisation should be " \
                     b"completed.</body></html>"
    return base_page


def prepare_auth(auth_url, kwargs):
    Timer(0.5, lambda: webbrowser.open(auth_url.format(**kwargs))).start()
