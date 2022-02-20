import socket
import pickle

from app.common import configure_logging, serialize, deserialize, Signal


class client:
    def __init__(self, name, port, debug=False, max_contacts=5):
        self.name = name
        self.port = port
        self.server_socket = socket.socket()
        self.client_send_socket = socket.socket()
        self.client_recv_socket = socket.socket()
        self.ip_address = socket.gethostbyname(socket.gethostname())
        self.client_recv_socket.bind((self.ip_address, port))
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
            self.server_socket.send(serialize(self.name))
            resp = self.server_socket.recv(1024)
            if deserialize(resp) == "":
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
        self.server_socket.send(serialize(Signal.DISCONNECT.value))
        self.server_socket.close()
        self.log.debug("Disconnected.")

    def __resolve_client_name(self, name):
        self.log.debug(f"Resolving {name} to ip address and port.")
        self.server_socket.send(serialize(Signal.RESOLVE_NAME.value))
        self.server_socket.recv(1024)
        self.server_socket.send(serialize(name))
        return pickle.loads(self.server_socket.recv(1024))

    def send_msg_to_client(self, client, msg):
        self.log.debug(f"Sending msg to {client}")
        try:
            ip, port = self.__resolve_client_name(client)
            if ip and port:
                client_send_socket = socket.socket()
                client_send_socket.connect((ip, port))
                client_send_socket.send(serialize(f"{self.name}: {msg}"))
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
                msg = deserialize(client_socket.recv(1024))
                if not msg:
                    self.log.debug("Stopped.")
                    break
                self.log.info(msg)
                client_socket.close()
        except Exception as e:
            self.log.error(e)
            pass

    def stop_listening(self):
        self.log.debug("Stopping listening for msgs.")
        tmp_socket = socket.socket()
        tmp_socket.connect((self.ip_address, self.port))
        self.client_recv_socket.close()
        tmp_socket.close()

    def get_clients_status(self):
        self.server_socket.send(serialize(Signal.GET_STATUS.value))
        return pickle.loads(self.server_socket.recv(1024))

    def get_logger(self):
        return self.log
