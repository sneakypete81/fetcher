import logging
from typing import Union

logger = logging.getLogger("fetch")


def trace(prefix: str, data: Union[str, bytes]):
    if isinstance(data, bytes):
        data = data.decode("ascii")

    for line in data.splitlines():
        logger.info(f"{prefix} {line}")
