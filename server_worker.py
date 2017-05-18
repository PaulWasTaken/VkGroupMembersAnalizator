import socket
import webbrowser

from formatter import extract_code, parse_members, parse_token
from select import select
from threading import Timer
from time import time
from urllib.request import urlopen


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

    @staticmethod
    def get_group_members(group_id, token, version):
        current_pos = 0
        total_amount = 9223372036854775807
        while current_pos != total_amount:
            resp = VkWorker.get_url_response(
                VkWorker.api_url,
                {"method": "groups.getMembers",
                 "params": "group_id={id}&offset={offset}&fields=bdate"
                 .format(id=group_id, offset=current_pos),
                 "token": token,
                 "api_version": version}
            )
            total_amount, ids = parse_members(resp)
            current_pos += len(ids)
            for member in ids:
                yield member

    @staticmethod
    def get_access_token(id_, port, api_version, key):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("localhost", port))
            sock.listen()
            base_page = VkWorker.get_base_page()
            VkWorker.prepare_auth(VkWorker.auth_url,
                                  {"id": id_, "port": port,
                                   "api_version": api_version})
            code = VkWorker.get_code(sock, base_page)
            if code:
                data = VkWorker.get_url_response(VkWorker.token_url,
                                                 {"id": id_,
                                                  "secret": key,
                                                  "port": port,
                                                  "code": code})
                return parse_token(data)
            else:
                raise ConnectionError

    @staticmethod
    def prepare_auth(auth_url, kwargs):
        Timer(0.5, lambda: webbrowser.open(auth_url.format(**kwargs))).start()

    @staticmethod
    def get_url_response(url, kwargs):
        with urlopen(url.format(**kwargs)) as response:
            return response.read().decode()

    @staticmethod
    def get_code(sock, base_page):
        data = VkWorker.receive_data(sock, base_page)
        return extract_code(data)

    @staticmethod
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
        raise socket.timeout

    @staticmethod
    def get_base_page():
        base_page = b"HTTP/1.1 200 OK\r\n" \
                    b"Content-Type: text\html; " \
                    b"charset=utf-8\r\n\r\n"
        try:
            with open("base_page.html", "rb") as reader:
                base_page += reader.read()
        except IOError:
            base_page += b"<html><body>Sorry, no base page was " \
                         b"found</body></html>"
        return base_page
