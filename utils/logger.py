import logging
import os
from pathlib import Path

# Bring in the dynamic application configuration instance
from config.settings import settings

# Internal tracking flag to ensure configuration executes exactly once per runtime
_is_configured = False

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def _setup_global_logging() -> None:
    """
    Initializes and configures the root logging infrastructure dynamically.
    Fetches runtime thresholds, file paths, and console toggles directly from 
    the central configuration subsystem.
    """
    global _is_configured
    if _is_configured:
        return

    # 1. Dynamically read configurations from the settings abstraction layer
    log_file_path = Path(settings.logging_file)
    log_level_str = settings.logging_level.upper()
    enable_console = settings.console_logging_enabled

    # Map the string log level from config to Python's internal logging constants
    # Fallback to logging.INFO if an invalid string is passed
    numeric_level = getattr(logging, log_level_str, logging.INFO)

    # 2. Automatically bootstrap the directory structure for logs if missing
    if log_file_path.parent:
        os.makedirs(log_file_path.parent, exist_ok=True)

    root_logger = logging.getLogger()

    # 3. SAFEGUARD: If the root logger already has handlers (e.g., in pytest), respect them
    if not root_logger.handlers:
        formatter = logging.Formatter(LOG_FORMAT)
        root_logger.setLevel(logging.DEBUG)  # Root catches all; handlers filter down

        # 4. Conditionally attach the Console (Stream) Handler
        if enable_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(numeric_level)
            root_logger.addHandler(console_handler)

        # 5. Configure and attach the permanent File Handler
        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(numeric_level)
        root_logger.addHandler(file_handler)

    _is_configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Retrieves a named, fully configured tracking instance for any module.
    Automatically triggers the foundational logging layer on its first call.

    Args:
        name (str): Typically passing __name__ to represent the current module context.

    Returns:
        logging.Logger: System-configured tracker object ready for use.
    """
    _setup_global_logging()
    return logging.getLogger(name)