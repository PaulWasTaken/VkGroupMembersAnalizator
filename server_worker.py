import socket

from formatter import parse_members, parse_token, extract_total, extract_code
from methods.methods import get_base_page, get_url_response, prepare_auth, \
    receive_data
from printer import print_progress
from urllib.parse import quote


def get_code(sock, base_page):
    data = receive_data(sock, base_page)
    return extract_code(data)


def form_exec_request(start, group):
    methods_list = []
    for i in range(20):
        methods_list.append('''
        API.groups.getMembers(
            {{"fields": "bdate",
            "group_id":"{}",
            "offset":"{}"}})'''.format(group, str(start + i * 1000)))
    return quote("return [{}];".format(",".join(
        [method.replace("\n", "").replace(" ", "")
         for method in methods_list])))


class VkWorker:
    auth_url = "https://oauth.vk.com/authorize?client_id={id}" \
               "&scope=audio&redirect_uri=http://localhost:{port}" \
               "&v={api_version}&response_type=code"
    token_url = "https://oauth.vk.com/access_token?" \
                "client_id={id}&" \
                "client_secret={secret}&" \
                "redirect_uri=http://localhost:{port}&" \
                "code={code}"
    api_url = "https://api.vk.com/method/{method}" \
              "?{params}&access_token={token}&v={api_version}"
    api_execute_url = "https://api.vk.com/method/execute?" \
                      "code={code}&version={api_version}&access_token={token}"

    def __init__(self, id_, key, group_id, version):
        self.id_ = id_
        self.key = key
        self.group_id = group_id
        self.version = version
        self.token = None
        self.time_left = None
        self.user_id = None

    def make_prep(self):
        current_pos = 0
        resp = get_url_response(
            VkWorker.api_url,
            {"method": "groups.getMembers",
             "params": "group_id={id}&count=1".format(id=self.group_id),
             "token": self.token,
             "api_version": self.version}
        )
        total_amount = extract_total(resp)
        printer = print_progress()
        printer.send(None)
        return current_pos, total_amount, printer

    def get_group_members(self):
        current_pos, total_amount, printer = self.make_prep()
        while current_pos < total_amount:
            resp = self.get_response(current_pos, total_amount)
            ids = parse_members(resp)
            current_pos += len(ids)
            printer.send((current_pos, total_amount))
            for member in ids:
                yield member

    def get_response(self, current_pos, total_amount):
        if total_amount > 90000:
            code = form_exec_request(current_pos, self.group_id)
            return get_url_response(
                VkWorker.api_execute_url,
                {"code": code,
                 "token": self.token,
                 "api_version": self.version})
        else:
            return get_url_response(
                VkWorker.api_url,
                {"method": "groups.getMembers",
                 "params": "group_id={id}&offset={offset}&fields=bdate"
                 .format(id=self.group_id, offset=current_pos),
                 "token": self.token,
                 "api_version": self.version})

    def get_access_token(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("localhost", port))
            sock.listen()
            base_page = get_base_page("base_page.html")
            prepare_auth(VkWorker.auth_url,
                         {"id": self.id_, "port": port,
                          "api_version": self.version})
            auth_code = get_code(sock, base_page)
            if auth_code:
                data = get_url_response(VkWorker.token_url,
                                        {"id": self.id_,
                                         "secret": self.key,
                                         "port": port,
                                         "code": auth_code})
                self.token, self.time_left, self.user_id = parse_token(data)
            else:
                raise ConnectionError
