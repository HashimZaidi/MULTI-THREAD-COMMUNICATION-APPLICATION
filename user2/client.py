import socket
import pickle
from threading import Thread
import re


class user:
    def __init__(self, name, ip, port, max_contacts=5):
        self.name = name
        self.server_socket = socket.socket()
        self.client_send_socket = socket.socket()
        self.client_recv_socket = socket.socket()
        self.client_recv_socket.bind((ip, port))
        self.client_recv_socket.listen(max_contacts)

    def connect_to_server(self, ip, port):
        self.server_socket.connect((ip, port))
        self.server_socket.send(self.name.encode())
        self.server_socket.recv(1024)
        addr = self.client_recv_socket.getsockname()
        self.server_socket.send(pickle.dumps(addr))
        print(f"***{self.name} is now connected to the server***")

    def disconnect_from_server(self):
        print("Disconnecting...")
        self.server_socket.send("disconnect".encode())
        self.server_socket.close()

    def __resolve_user_name(self, name):
        self.server_socket.send("resolve_name".encode())
        self.server_socket.recv(1024)
        self.server_socket.send(name.encode())
        return pickle.loads(self.server_socket.recv(1024))

    def send_msg_to_user(self, user, msg):
        try:
            ip, port = self.__resolve_user_name(user)
            if ip and port:
                client_send_socket = socket.socket()
                client_send_socket.connect((ip, port))
                client_send_socket.send(f"{self.name}: {msg}".encode())
                client_send_socket.close()
                return "True"
            else:
                print(f"Either {user} does not exists or is not online")
                return False
        except Exception as e:
            print(e)
            return False

    def listen(self):
        try:
            while True:
                user_socket, _ = self.client_recv_socket.accept()
                msg = user_socket.recv(1024).decode()
                print(msg)
                user_socket.close()
        except ConnectionAbortedError:
            pass

    def get_users_status(self):
        self.server_socket.send("get_status".encode())
        return pickle.loads(self.server_socket.recv(1024))


if __name__ == "__main__":
    u = user("user2", "127.0.0.1", 8002)
    u.connect_to_server("127.0.0.1", 8000)
    listen = Thread(target=u.listen)
    listen.start()
    while True:
        usr_inp = input(
            "Enter 1 to send message\n"
            + "Enter 2 to view who's online/offline\n"
            + "Enter 3 to exit\n"
        )
        if usr_inp == "1":
            while True:
                usr_inp = input(
                    "Enter in the following format:\n"
                    + "'Name:Message'\n"
                    + "or Enter Exit to the main menu\n"
                )
                if usr_inp == "Exit":
                    break
                match = re.match("^\w+:.+$", usr_inp)
                if bool(match):
                    i = usr_inp.index(":")
                    name = usr_inp[:i]
                    msg = usr_inp[i + 1 :]
                    msg_sent = u.send_msg_to_user(name, msg)
                    print("Sent") if msg_sent else print(
                        f"Unable to send msg to {name}"
                    )
                else:
                    print("Invalid Format")
        elif usr_inp == "2":
            print(u.get_users_status())
        elif usr_inp == "3":
            u.disconnect_from_server()
            u.client_recv_socket.close()
            listen.join()
            break
        else:
            print("Invalid option")
