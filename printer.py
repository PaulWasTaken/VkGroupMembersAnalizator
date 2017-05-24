from sys import stdout


def print_progress():
    to_write = ""
    while 1:
        current, total = yield
        percent = round((current / total) * 100, 2)
        stdout.write("\r" + " " * len(to_write))
        stdout.flush()
        to_write = "{amount}% was processed.".format(amount=percent)
        stdout.write("\r" + to_write)
        stdout.flush()
        if current == total:
            break
