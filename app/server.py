import socket
import pickle
import _thread as thread
from os.path import join
from app.logger import configure_logging


class client_props:
    def __init__(self, socket, addr) -> None:
        self.socket = socket
        self.addr = addr

    def get_socket(self):
        return self.socket

    def get_addr(self):
        return self.addr


class server:
    _clients_data_file_name = "clients_data.txt"

    def __init__(self, port, debug=False, clients_data_dir="/tmp", max_clients=5):
        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(("", port))
        self.socket.listen(max_clients)
        self.online_clients = {}
        self.clients_data_file_path = join(
            clients_data_dir, self._clients_data_file_name
        )
        self.log = configure_logging(debug)

    def listen_and_serve(self):
        self.log.info("Waiting for new connections")
        while True:
            client_socket, _ = self.socket.accept()
            self.log.debug(f"New connection: {client_socket}")
            client_name = client_socket.recv(1024).decode()
            self.log.debug(f"{client_socket} is trying to register with the name, {client_name}.")
            if client_name in self.online_clients.keys():
                self.log.debug(f"Another client exists with the name, {client_name}.")
                client_socket.close()
                continue
            else:
                client_socket.send("ack".encode())
            addr = pickle.loads(client_socket.recv(1024))
            self.register_client(client_name)
            self.online_clients[client_name] = client_props(client_socket, addr)
            thread.start_new_thread(self.serve_client, (client_name,))

    def register_client(self, client_name):
        self.log.debug(f"Writing {client_name} to {self.clients_data_file_path}.")
        with open(self.clients_data_file_path, "a+") as clients_data_file:
            clients_data_file.seek(0)
            clients = clients_data_file.read().split("\n")
            if client_name not in clients:
                clients_data_file.seek(0, 2)
                clients_data_file.write(client_name + "\n")

    def check_clients_status(self):
        self.log.debug("Checking clients status ...")
        client_status = dict(
            (client, "Online") for client in self.online_clients.keys()
        )
        self.log.debug(f"Reading from {self.clients_data_file_path}.")
        with open(self.clients_data_file_path, "r") as clients_data_file:
            all_clients = (clients_data_file.read().split("\n"))[:-1]
            for client in all_clients:
                if client not in client_status:
                    client_status[client] = "Offline"
        return client_status

    def serve_client(self, client_name):
        self.log.info(
            f"{client_name}({self.online_clients[client_name].get_addr()}) is Online"
        )
        self.log.info(f"ACTIVE CLIENTS: {list(self.online_clients.keys())}")
        client_socket = self.online_clients[client_name].get_socket()
        while True:
            try:
                sgnl = client_socket.recv(1024).decode()

                if sgnl == "":
                    raise ConnectionError

                self.log.info(f"{client_name}: {sgnl}")
                if sgnl == "disconnect":
                    self.log.info(f"{client_name} disconnected")
                    del self.online_clients[client_name]
                    client_socket.close()
                    self.log.info(f"ACTIVE CLIENTS: {list(self.online_clients.keys())}")
                    break
                elif sgnl == "resolve_name":
                    client_socket.send("ack".encode())
                    name = client_socket.recv(1024).decode()
                    self.log.info(f"Resolving {name} ...")
                    if name in self.online_clients:
                        addr = self.online_clients[name].get_addr()
                        self.log.info(f"{name} => {addr}")
                        addr_str_enc = pickle.dumps(addr)
                        client_socket.send(addr_str_enc)
                    else:
                        self.log.info("Client not found/online.")
                        client_socket.send(pickle.dumps((None, None)))
                elif sgnl == "get_status":
                    clients_status = self.check_clients_status()
                    client_socket.send(pickle.dumps(clients_status))
                else:
                    self.log.info(f"Invalid request from client: {client_name}")

            except ConnectionError:
                self.log.info(f"{client_name} unexpectedly got disconnected")
                del self.online_clients[client_name]
                client_socket.close()
                self.log.info(f"ACTIVE CLIENTS: {list(self.online_clients.keys())}")
                break
