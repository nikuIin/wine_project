from logging import Formatter, Logger, getLogger
from logging.handlers import TimedRotatingFileHandler
from os import mkdir, path

from core.config import log_settings
from core.logger.filters import SensitiveWordsFilter


def get_configure_logger(filename: str, log_level: int = log_settings.log_level) -> Logger:
    """
    Configure logger with the given filename.

    Args:
        filename (str): The name of the log file.
        log_level (str): The log level to use (default taking by the cofiguration project file).

    Returns:
        Logger: The configured logger.
    """
    filename = filename.lower()
    logger = getLogger(filename)
    logger.setLevel(log_level)
    if logger.hasHandlers():
        # Avoid reconfiguring logger if it already exists
        return logger

    # Create log directory if it doesn't exist
    try:
        if not path.isdir(log_settings.log_directory):
            mkdir(log_settings.log_directory)
    except OSError as error:
        logger.error(
            "Error with creating the log directory %r: %s", log_settings.log_directory, error
        )

    log_formatter = Formatter(fmt=log_settings.log_format, datefmt=log_settings.date_format)

    safe_filename = filename.replace(".", "_") + ".log"
    log_file_path = path.join(log_settings.log_directory, safe_filename)

    # Configure and add handler and filters
    try:
        handler = TimedRotatingFileHandler(
            filename=log_file_path,
            when=log_settings.log_roating,
            backupCount=log_settings.backup_count,
            utc=log_settings.utc,
            encoding="utf-8",
        )
        handler.setFormatter(log_formatter)

        # use this filter if you want see the logs in the console
        # (import it from the file filters.py in the core/logger/ directory)
        # logger.addFilter(ColorFilter())  # noqa: ERA001

        # Add sensitive words filter
        logger.addFilter(SensitiveWordsFilter())

        logger.addHandler(handler)

        logger.debug(
            "Logger %r successfully configured. Logger level: %s. Logger file: %r",
            filename,
            log_level,
            log_file_path,
        )

    except Exception as error:
        logger.error(
            "The error is ocured during the logger configuration. Logger %r: %s",
            logger,
            error,
        )
    return logger
