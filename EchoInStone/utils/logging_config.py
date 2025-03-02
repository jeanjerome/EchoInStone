import logging
from logging.handlers import RotatingFileHandler

def configure_logging(log_level=logging.INFO):
    """
    Configures the logging for the entire project.

    :param log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    log_file = 'app.log'

    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Check if handlers already exist to avoid duplicates
    has_console_handler = any(isinstance(h, logging.StreamHandler) for h in logger.handlers)
    has_file_handler = any(isinstance(h, RotatingFileHandler) for h in logger.handlers)

    # Add console handler if not already present
    if not has_console_handler:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(console_handler)

    # Add file handler if not already present
    if not has_file_handler:
        file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(file_handler)

    # Reduce log verbosity for external libraries to avoid noise
    external_loggers = ["urllib3", "pytubefix", "fsspec", "pydub", "numba"]
    for ext_logger in external_loggers:
        logging.getLogger(ext_logger).setLevel(logging.WARNING)

    # Test logs to confirm configuration
    logger.info(f"Handlers configured: {[type(h).__name__ for h in logger.handlers]}")
    logger.info(f"Logging level set to: {logging.getLevelName(log_level)}")


    if log_level == logging.DEBUG:
        logger.debug("⚡ DEBUG mode enabled: Detailed logs will be displayed, including external dependencies.")
        logger.debug("⚡ If the logs are too verbose, consider using logging.INFO or higher.")