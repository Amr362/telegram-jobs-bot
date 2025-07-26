import logging
import os
from loguru import logger

class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

def setup_logger(log_level: str = "INFO", log_file: str = None):
    """Configures the logging system for the application.

    Args:
        log_level (str): The minimum logging level (e.g., 'INFO', 'DEBUG', 'ERROR').
        log_file (str, optional): Path to the log file. If None, logs only to console.
    """
    # Remove default handler to avoid duplicate logs
    logger.remove()

    # Add console handler
    logger.add(
        os.sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
        enqueue=True
    )

    # Add file handler if log_file is provided
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        logger.add(
            log_file,
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="10 MB",  # Rotate log file every 10 MB
            compression="zip",  # Compress old log files
            enqueue=True
        )

    # Intercept standard logging messages and redirect to Loguru
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    logging.getLogger("uvicorn").handlers = [InterceptHandler()]
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
    logging.getLogger("httpx").handlers = [InterceptHandler()]
    logging.getLogger("telegram").handlers = [InterceptHandler()]

def get_logger(name: str):
    """Returns a Loguru logger instance for a given name.

    Args:
        name (str): The name of the logger (usually __name__ of the module).

    Returns:
        loguru.logger: The logger instance.
    """
    return logger.bind(name=name)


