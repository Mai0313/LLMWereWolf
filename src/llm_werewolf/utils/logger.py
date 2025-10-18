"""Logging utilities for the Werewolf game."""

from typing import Any
import logging
from pathlib import Path


def setup_logger(
    name: str = "werewolf", level: int = logging.INFO, log_file: str | Path | None = None
) -> logging.Logger:
    """Set up a logger for the game.

    Args:
        name: Name of the logger.
        level: Logging level.
        log_file: Optional file path to write logs to.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Default logger instance
default_logger = setup_logger()


def log_game_event(event_type: str, message: str, **kwargs: Any) -> None:  # noqa: ANN401
    """Log a game event.

    Args:
        event_type: Type of the event.
        message: Event message.
        **kwargs: Additional event data.
    """
    extra_info = " ".join([f"{k}={v}" for k, v in kwargs.items()])
    log_message = f"[{event_type}] {message}"
    if extra_info:
        log_message += f" ({extra_info})"

    default_logger.info(log_message)


def log_error(error: Exception, context: str = "") -> None:
    """Log an error with context.

    Args:
        error: The exception that occurred.
        context: Additional context about when the error occurred.
    """
    if context:
        default_logger.error(f"{context}: {error}")
    else:
        default_logger.error(str(error))
