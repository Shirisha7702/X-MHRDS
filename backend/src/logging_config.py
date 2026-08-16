import logging
import sys

_ROOT_NAME = "xmhrds"
_configured = False


def configure_logging(level=logging.INFO):
    """Idempotent: safe to call from every module that wants a logger, only the first
    call actually attaches a handler."""
    global _configured
    root = logging.getLogger(_ROOT_NAME)
    if _configured:
        return root

    root.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    ))
    root.addHandler(handler)
    root.propagate = False
    _configured = True
    return root


def get_logger(name):
    """Returns a logger under the shared 'xmhrds' namespace, e.g. get_logger('sandbox')
    -> 'xmhrds.sandbox'. Configures the shared root handler on first use."""
    configure_logging()
    return logging.getLogger(f"{_ROOT_NAME}.{name}")
