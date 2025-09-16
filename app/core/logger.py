import logging

from .config import settings

def setup_logging():
    logging.basicConfig(
        level=settings.logging.log_level.upper(),
        format=settings.logging.log_format,
    )
    logger = logging.getLogger('ai_replies')
    return logger


logger = setup_logging()