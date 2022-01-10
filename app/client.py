import socket
import pickle

from app.logger import configure_logging


class client:
    def __init__(self, name, port, debug=False, max_contacts=5):
        self.name = name
        self.server_socket = socket.socket()
        self.client_send_socket = socket.socket()
        self.client_recv_socket = socket.socket()
        self.client_recv_socket.bind(("", port))
        self.client_recv_socket.listen(max_contacts)
        self.log = configure_logging(debug)

    def connect_to_server(self, ip, port):
        try:
            self.log.debug(f"Connecting to the server ({ip},{port}) ...")
            self.server_socket.connect((ip, port))
            self.log.debug("Connected.")
            self.log.debug(
                f"Registering client on the server with the name, {self.name}."
            )
            self.server_socket.send(self.name.encode())
            resp = self.server_socket.recv(1024)
            if resp.decode() == "":
                self.log.error(
                    "The name is already in use. Please register with a different name."
                )
                return False
            self.log.debug(f"Registered.")
            addr = self.client_recv_socket.getsockname()
            self.log.debug(f"Sending client's address: {addr} to the server.")
            self.server_socket.send(pickle.dumps(addr))
            self.log.info(f"{self.name} is now connected to the server")
            return True
        except Exception as e:
            self.log.error(f"Unable to connect to the server. {str(e)}")
            return False

    def disconnect_from_server(self):
        self.log.info("Disconnecting...")
        self.server_socket.send("disconnect".encode())
        self.server_socket.close()

    def __resolve_client_name(self, name):
        self.log.debug(f"Resolving {name} to ip address and port.")
        self.server_socket.send("resolve_name".encode())
        self.server_socket.recv(1024)
        self.server_socket.send(name.encode())
        return pickle.loads(self.server_socket.recv(1024))

    def send_msg_to_client(self, client, msg):
        self.log.debug(f"{msg} => {client}")
        try:
            ip, port = self.__resolve_client_name(client)
            if ip and port:
                client_send_socket = socket.socket()
                client_send_socket.connect((ip, port))
                client_send_socket.send(f"{self.name}: {msg}".encode())
                client_send_socket.close()
                self.log.info("Sent")
                return "True"
            else:
                self.log.error(
                    f"Unable to send msg to {client} \nEither a client with the name, {client}, does not exists or the client is not online.",
                )
                return False
        except Exception as e:
            self.log.error(f"Unable to send msg to {client}. {str(e)}")
            return False

    def listen(self):
        self.log.debug("Listening for messages from other clients.")
        try:
            while True:
                client_socket, _ = self.client_recv_socket.accept()
                msg = client_socket.recv(1024).decode()
                self.log.info(msg)
                client_socket.close()
        except ConnectionAbortedError:
            pass

    def get_clients_status(self):
        self.server_socket.send("get_status".encode())
        return pickle.loads(self.server_socket.recv(1024))

    def get_logger(self):
        return self.log
