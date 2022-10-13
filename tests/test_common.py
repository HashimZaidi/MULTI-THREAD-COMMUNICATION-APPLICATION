import unittest

from app.common import Signal, serialize, deserialize


class TestCommon(unittest.TestCase):
    def test_Signals(self):
        self.assertEqual(Signal.DISCONNECT.value, "1")
        self.assertEqual(Signal.RESOLVE_NAME.value, "2")
        self.assertEqual(Signal.GET_STATUS.value, "3")
        self.assertEqual(Signal.ACK.value, "4")

    def test_serialize(self):
        self.assertEqual(serialize("Hello, World!"), "Hello, World!".encode())

    def test_deserialize(self):
        self.assertEqual(deserialize(serialize("Hello, World!")), "Hello, World!")