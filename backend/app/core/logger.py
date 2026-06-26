import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger for the given module name.

    Usage:
        from app.core.logger import get_logger
        logger = get_logger(__name__)

        logger.info("Meeting created: id=%s", meeting.id)
        logger.warning("Assignee not found: %s", assignee_name)
        logger.error("Unexpected error", exc_info=True)
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.propagate = False

    return logger
