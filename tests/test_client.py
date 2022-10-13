import unittest
from mock import patch, Mock


from app.client import client
from app.common import Signal, serialize


class TestClient(unittest.TestCase):
    @patch("socket.gethostbyname")
    @patch("socket.socket")
    def setUp(self, mock_socket, mock_gethostbyname):
        mock_gethostbyname.return_value = "localhost"
        self.test_client = client("testClient", 8001, debug=True)

    def tearDown(self):
        self.__delattr__("test_client")
        return super().tearDown()

    def test_clientInit_shouldBeSuccessful(self):
        self.assertEqual(self.test_client.name, "testClient")
        self.assertEqual(self.test_client.port, 8001)
        self.assertEqual(self.test_client.ip_address, "localhost")

    @patch("pickle.loads")
    @patch("pickle.dumps")
    def test_connectToServer_shouldReturnTrue(self, mock_dumps, mock_loads):
        mock_dumps.return_value = ""
        mock_loads.return_value = ""
        self.test_client.server_socket.recv.return_value = serialize(Signal.ACK.value)
        self.assertTrue(self.test_client.connect_to_server("localhost", 8000))

    @patch("pickle.loads")
    @patch("pickle.dumps")
    def test_connectToServer_shouldReturnFalse_whenClientNameExists(
        self, mock_dumps, mock_loads
    ):
        mock_dumps.return_value = ""
        mock_loads.return_value = ""
        self.test_client.server_socket.recv.return_value = serialize("")
        self.assertFalse(self.test_client.connect_to_server("localhost", 8000))

    @patch("pickle.loads")
    @patch("pickle.dumps")
    def test_connectToServer_shouldReturnFalse_whenServerUnavailable(
        self, mock_dumps, mock_loads
    ):
        mock_dumps.return_value = ""
        mock_loads.return_value = ""
        self.test_client.server_socket.connect.side_effect = Exception
        self.assertFalse(self.test_client.connect_to_server("localhost", 8000))

    def test_disconnectFromServer_shouldBeSuccessful(self):
        self.assertIsNone(self.test_client.disconnect_from_server())

    @patch("socket.socket")
    @patch("pickle.loads")
    def test_sendMsg_shouldReturnTrue_whenClientOnline(self, mock_loads, mock_socket):
        mock_loads.return_value = ("localhost", 8002)
        self.assertTrue(
            self.test_client.send_msg_to_client("AnotherTestClient", "Hello, World!")
        )

    @patch("socket.socket")
    @patch("pickle.loads")
    def test_sendMsg_shouldReturnFalse_whenClientOffline(self, mock_loads, mock_socket):
        mock_loads.return_value = (None, None)
        self.assertFalse(
            self.test_client.send_msg_to_client("AnotherTestclient", "Hello, World!")
        )

    @patch("socket.socket")
    @patch("pickle.loads")
    def test_sendMsg_shouldReturnFalse_onException(self, mock_loads, mock_socket):
        mock_loads.return_value = ("localhost", 8002)
        mock_socket.side_effect = Exception
        self.assertFalse(
            self.test_client.send_msg_to_client("AnotherTestclient", "Hello, World!")
        )

    def test_listen_shouldReturn_whenStopSignalReceived(self):
        mock_socket = Mock()
        mock_socket.recv.return_value = serialize("")
        self.test_client.client_recv_socket.accept.return_value = (mock_socket, None)
        self.assertIsNone(self.test_client.listen())

    def test_listen_shouldReturn_OnException(self):
        self.test_client.client_recv_socket.accept.side_effect = Exception
        self.assertIsNone(self.test_client.listen())

    @patch("socket.socket")
    def test_stopListening_shouldBeSuccessful(self, mock_socket):
        self.assertIsNone(self.test_client.stop_listening())

    @patch("pickle.loads")
    def test_getClientsStatus_shouldBeSuccessful(self, mock_loads):
        client_status = {"testClient": "Online", "AnotherTestClient": "Offline"}
        mock_loads.return_value = client_status
        self.assertDictEqual(self.test_client.get_clients_status(), client_status)

    def test_getLogger_shouldBeSuccessful(self):
        self.assertEqual(self.test_client.log, self.test_client.get_logger())
