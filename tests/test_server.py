from asyncore import write
from atexit import register
import unittest
from unittest.mock import Mock
from mock import patch, mock_open

import os
from app.common import Signal, serialize
from app.server import server, client_props


class TestServer(unittest.TestCase):
    @patch("socket.create_server")
    def setUp(self, mock_create_server):
        self.test_server = server("8000", debug=True)

    def tearDown(self):
        self.__delattr__("test_server")
        return super().tearDown

    def test_serverInit_shouldBeSuccessful(self):
        self.assertDictEqual(self.test_server.online_clients, {})
        self.assertEqual(
            self.test_server.clients_data_file_path, "/tmp/clients_data.txt"
        )

    @patch("app.server.open")
    def test_registerClient_shouldBeSuccessful(self, mock_opener):
        registered_clients = []

        def write_to_file(client_name):
            registered_clients.append(client_name[:-1])

        mock_opener.side_effect = mock_open()
        mock_opener().write.side_effect = write_to_file

        self.test_server.register_client("testClient")
        self.test_server.register_client("AnotherTestClient")

        self.assertEqual(registered_clients[0], "testClient")
        self.assertEqual(registered_clients[1], "AnotherTestClient")
        self.assertEqual(len(registered_clients), 2)

    @patch("app.server.open")
    def test_registerClient_ignore_whenDuplicate(self, mock_opener):
        mock_opener.side_effect = mock_open(read_data="testClient")
        self.test_server.register_client("testClient")
        mock_opener().write.assert_not_called()

    @patch("app.server.open")
    def test_checkClientsStatus_shouldBeSuccessful(self, mock_opener):
        registered_clients = ["testClient1", "testClient2", "testClient3"]
        self.test_server.online_clients["testClient1"] = client_props(
            Mock(), ("localhost", 8001)
        )
        mock_opener.side_effect = mock_open(
            read_data="\n".join(registered_clients) + "\n"
        )
        clients_status = self.test_server.check_clients_status()
        self.assertEqual(clients_status["testClient1"], "Online")
        self.assertEqual(clients_status["testClient2"], "Offline")
        self.assertEqual(clients_status["testClient3"], "Offline")

    def test_serveClient_shouldReturn_whenClientDisconnects(self):
        mock_socket = Mock()
        mock_socket.recv.return_value = serialize(Signal.DISCONNECT.value)
        self.test_server.online_clients["testClient"] = client_props(
            mock_socket, ("localhost", 8001)
        )
        self.test_server.serve_client("testClient")

    def test_serveClient_shouldReturn_OnException(self):
        mock_socket = Mock()
        mock_socket.recv.return_value = serialize("")
        self.test_server.online_clients["testClient"] = client_props(
            mock_socket, ("localhost", 8001)
        )
        self.test_server.serve_client("testClient")

    @patch("pickle.dumps")
    def test_serveClient_resolveName_shouldReturnNoneTuple_whenClientOffline(
        self, mock_dumps
    ):
        mock_dumps.side_effect = lambda x: x
        res = {"addr": tuple()}

        def send_addr_to_client(arg):
            if type(arg) == str:
                return
            res["addr"] = arg

        mock_socket = Mock()
        mock_socket.recv.side_effect = [
            serialize(Signal.RESOLVE_NAME.value),
            serialize("testClient2"),
            serialize(Signal.DISCONNECT.value),
        ]
        mock_socket.send.side_effect = send_addr_to_client

        self.test_server.online_clients["testClient1"] = client_props(
            mock_socket, ("localhost", 8001)
        )
        self.test_server.serve_client("testClient1")
        self.assertTupleEqual(res["addr"], (None, None))

    @patch("pickle.dumps")
    def test_serveClient_resolveName_shouldReturnAddr_whenClientOnline(
        self, mock_dumps
    ):
        mock_dumps.side_effect = lambda x: x
        res = {"addr": tuple()}

        def send_addr_to_client(arg):
            if type(arg) == str:
                return
            res["addr"] = arg

        mock_socket = Mock()
        mock_socket.recv.side_effect = [
            serialize(Signal.RESOLVE_NAME.value),
            serialize("testClient2"),
            serialize(Signal.DISCONNECT.value),
        ]
        mock_socket.send.side_effect = send_addr_to_client

        self.test_server.online_clients["testClient1"] = client_props(
            mock_socket, ("localhost", 8001)
        )
        self.test_server.online_clients["testClient2"] = client_props(
            mock_socket, ("localhost", 8002)
        )
        self.test_server.serve_client("testClient1")
        self.assertTupleEqual(res["addr"], ("localhost", 8002))

    @patch("pickle.dumps")
    @patch("app.server.open")
    def test_serveClient_getStatus_shouldBeSuccessful(self, mock_opener, mock_dumps):
        mock_dumps.side_effect = lambda x: x
        res = {"status": dict()}

        def send_status_to_client(arg):
            res["status"] = arg

        mock_socket = Mock()
        mock_socket.recv.side_effect = [
            serialize(Signal.GET_STATUS.value),
            serialize(Signal.DISCONNECT.value),
        ]
        mock_socket.send.side_effect = send_status_to_client

        registered_clients = ["testClient1", "testClient2", "testClient3"]
        self.test_server.online_clients["testClient1"] = client_props(
            mock_socket, ("localhost", 8001)
        )
        mock_opener.side_effect = mock_open(
            read_data="\n".join(registered_clients) + "\n"
        )
        clients_status = self.test_server.check_clients_status()
        self.assertEqual(clients_status["testClient1"], "Online")
        self.assertEqual(clients_status["testClient2"], "Offline")
        self.assertEqual(clients_status["testClient3"], "Offline")
