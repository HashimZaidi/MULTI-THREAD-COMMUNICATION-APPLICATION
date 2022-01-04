import socket
import pickle
import _thread as thread
import os


class user_props:
    def __init__(self, socket, addr) -> None:
        self.socket = socket
        self.addr = addr

    def get_socket(self):
        return self.socket

    def get_addr(self):
        return self.addr


class server:
    def __init__(
        self, ip, port, max_users=5, users_data_file_path="/tmp/users_data.txt"
    ):
        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((ip, port))
        self.socket.listen(max_users)
        self.online_users = {}
        self.users_data_file_path = users_data_file_path

    def listen_and_serve(self):
        print("Waiting for new connections")
        while True:
            client_socket, _ = self.socket.accept()
            user_name = client_socket.recv(1024).decode()
            client_socket.send("ack".encode())
            addr = pickle.loads(client_socket.recv(1024))
            self.register_user(user_name)
            self.online_users[user_name] = user_props(client_socket, addr)
            thread.start_new_thread(self.serve_user, (user_name,))

    def register_user(self, user_name):
        with open(self.users_data_file_path, "a+") as users_data_file:
            users_data_file.seek(0)
            users = users_data_file.read().split("\n")
            if user_name not in users:
                users_data_file.seek(0, 2)
                users_data_file.write(user_name + "\n")

    def check_users_status(self):
        user_status = dict((user, "Online") for user in self.online_users.keys())
        with open(self.users_data_file_path, "r") as users_data_file:
            all_users = (users_data_file.read().split("\n"))[:-1]
            for user in all_users:
                if user not in user_status:
                    user_status[user] = "Offline"
        return user_status

    def serve_user(self, user_name):
        print(f"{user_name}({self.online_users[user_name].get_addr()}) is Online")
        print(f"ACTIVE USERS: {list(self.online_users.keys())}")
        client_socket = self.online_users[user_name].get_socket()
        while True:
            try:
                sgnl = client_socket.recv(1024).decode()

                if sgnl == "":
                    raise ConnectionError

                if sgnl == "disconnect":
                    print(f"{user_name} disconnected")
                    del self.online_users[user_name]
                    client_socket.close()
                    print(f"ACTIVE USERS: {list(self.online_users.keys())}")
                    break
                elif sgnl == "resolve_name":
                    client_socket.send("ack".encode())
                    name = client_socket.recv(1024).decode()
                    if name in self.online_users:
                        addr_str_enc = pickle.dumps(self.online_users[name].get_addr())
                        client_socket.send(addr_str_enc)
                    else:
                        client_socket.send(pickle.dumps((None, None)))
                elif sgnl == "get_status":
                    users_status = self.check_users_status()
                    client_socket.send(pickle.dumps(users_status))
                else:
                    print(f"Invalid request from client: {user_name}")

            except ConnectionError:
                print(f"{user_name} unexpectedly got disconnected")
                del self.online_users[user_name]
                client_socket.close()
                print(f"ACTIVE USERS: {list(self.online_users.keys())}")
                break


if __name__ == "__main__":
    s = server("127.0.0.1", 8000)
    s.listen_and_serve()
