import logging
import logging.handlers
from typing import Optional


LOGGER = logging.getLogger("CloudStorageFileSystem")


def configure_logger(verbose: bool, service_label: Optional[str] = None, profile_name: Optional[str] = None):
    if service_label is None and profile_name is None:
        identity = "%(name)s"
    else:
        identity = f"{service_label} - {profile_name}"

    if verbose:
        LOGGER.setLevel(logging.DEBUG)
         # formatter = logging.Formatter(f"%(funcName)s [{identity}] %(levelname)s: %(message)s")
    else:
        LOGGER.setLevel(logging.INFO)
        # formatter = logging.Formatter(f"%(name)s [%(asctime)s] %(levelname)s - %(message)s")
    formatter = logging.Formatter(f"[{identity}] %(levelname)s: %(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    sys_handler = logging.handlers.SysLogHandler(address="/dev/log")
    sys_handler.setFormatter(formatter)

    for handler in LOGGER.handlers:
        LOGGER.removeHandler(handler)
    LOGGER.addHandler(stream_handler)
    LOGGER.addHandler(sys_handler)
