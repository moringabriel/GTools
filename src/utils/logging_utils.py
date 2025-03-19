# src/utils/logging_utils.py

"""
Logging utilities for GTools
This module provides logging setup and helper functions for GTools components.
"""

import os
import sys
import logging
import traceback
from pathlib import Path
from datetime import datetime

# Default log directory
DEFAULT_LOG_DIR = os.path.join(os.path.expanduser("~"), ".nuke", "GTools", "logs")

# Global logger cache to avoid creating multiple loggers for the same name
_loggers = {}


def setup_logging(
        name="GToolsShelf",
        level=logging.DEBUG,
        log_dir=None,
        log_to_console=True,
        max_log_files=10
):
    """
    Setup logging for the GTools application

    Args:
        name (str): Logger name
        level (int): Logging level (default: DEBUG)
        log_dir (str): Directory for log files (default: ~/.nuke/GTools/logs)
        log_to_console (bool): Whether to log to console (default: True)
        max_log_files (int): Maximum number of log files to keep (default: 10)

    Returns:
        logging.Logger: Configured logger
    """
    # Use cached logger if it exists
    if name in _loggers:
        return _loggers[name]

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Check if handlers already exist to avoid duplicates
    if logger.handlers:
        return logger

    # Create log directory
    if log_dir is None:
        log_dir = DEFAULT_LOG_DIR

    os.makedirs(log_dir, exist_ok=True)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create file handler with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"{name.lower()}_{timestamp}.log")

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Create console handler if requested
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Clean up old log files
    _cleanup_old_logs(log_dir, name.lower(), max_log_files)

    # Store in cache
    _loggers[name] = logger

    # Log initial info
    logger.info(f"Logging initialized for {name}")
    logger.info(f"Log file: {log_file}")

    return logger


def get_logger(name="GToolsShelf"):
    """
    Get or create a logger with the given name

    Args:
        name (str): Logger name

    Returns:
        logging.Logger: Logger instance
    """
    if name in _loggers:
        return _loggers[name]

    return setup_logging(name)


def log_exception(logger, message="An error occurred"):
    """
    Log an exception with traceback

    Args:
        logger (logging.Logger): Logger instance
        message (str): Error message prefix
    """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    tb_text = ''.join(tb_lines)

    logger.error(f"{message}:\n{tb_text}")


def _cleanup_old_logs(log_dir, prefix, max_files):
    """
    Delete old log files when too many accumulate

    Args:
        log_dir (str): Log directory
        prefix (str): Log file prefix
        max_files (int): Maximum number of log files to keep
    """
    try:
        log_files = [
            f for f in os.listdir(log_dir)
            if f.startswith(prefix) and f.endswith(".log")
        ]

        if len(log_files) <= max_files:
            return

        # Sort by modification time (oldest first)
        log_files.sort(
            key=lambda f: os.path.getmtime(os.path.join(log_dir, f))
        )

        # Delete oldest files
        for file_to_delete in log_files[:-max_files]:
            file_path = os.path.join(log_dir, file_to_delete)
            os.remove(file_path)
    except Exception as e:
        # Can't use logger here as we might be in the setup process
        print(f"Error cleaning up log files: {e}")


def test_logging():
    """
    Test function to verify the logging setup
    """
    logger = get_logger("LoggingTest")

    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

    try:
        # Generate an exception
        1 / 0
    except Exception:
        log_exception(logger, "Test exception")

    return logger.handlers[0].baseFilename


if __name__ == "__main__":
    # Run test if executed directly
    log_file = test_logging()
    print(f"Log file created: {log_file}")