import logging


def configure_logging(debug=False):
    log = logging.getLogger("default")
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO
    log.setLevel(level)
    output_handler = logging.StreamHandler()
    output_handler.setFormatter(logging.Formatter("%(asctime)s — %(message)s"))
    log.addHandler(output_handler)
    return log
