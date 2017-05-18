from json import loads
from re import findall


def parse_token(data):
    if "error" in data:
        raise ConnectionError  # Think
    res = loads(data)
    return res['access_token'], res['expires_in'], res['user_id']


def parse_members(data):
    if "error" in data:
        raise ConnectionError  # Think
    res = loads(data)
    return res['response']['count'], res['response']['items']


def extract_code(data):
    return findall("(?<==)[^ ]+", data)[0]
