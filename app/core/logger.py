import logging

from .config import settings


def setup_logging():
    logging.basicConfig(
        level=settings.logging.log_level.upper(),
        format=settings.logging.log_format,
    )
    return logging.getLogger('ai_replies')


logger = setup_logging()
