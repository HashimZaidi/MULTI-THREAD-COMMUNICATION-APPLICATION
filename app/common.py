from enum import Enum
import logging


def serialize(inp):
    return inp.encode()


def deserialize(inp):
    return inp.decode()


class Signal(Enum):
    DISCONNECT = "1"
    RESOLVE_NAME = "2"
    GET_STATUS = "3"
    ACK = "4"


def configure_logging(debug=False):
    log = logging.getLogger("default")
    if log.hasHandlers():
        return log
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO
    log.setLevel(level)
    output_handler = logging.StreamHandler()
    output_handler.setFormatter(logging.Formatter("%(asctime)s — %(message)s"))
    log.addHandler(output_handler)
    return log
