from json import loads, dump
from re import findall


class ParseError(Exception):
    pass


def pre_processing(func):
    def printer(data):
        res = loads(data)
        if "error" in res:
            with open('log.log', 'w') as outfile:
                dump(data, outfile)
            raise ParseError
        return func(res)
    return printer


@pre_processing
def parse_token(res):
    return res['access_token'], res['expires_in'], res['user_id']


@pre_processing
def extract_total(res):
    return int(res["response"]["count"])


@pre_processing
def parse_members(res):
    try:
        return res['response']['items']
    except TypeError:
        users = []
        for i in range(20):
            users.extend(res['response'][i]['users'])
        return users


def extract_code(data):
    return findall("(?<==)[^ ]+", data)[0]
