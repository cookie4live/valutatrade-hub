
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging():
    """Настраивает логирование с ротацией файлов."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logger = logging.getLogger("valutatrade_hub")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = RotatingFileHandler(
            log_dir / "actions.log",
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8",
        )

        formatter = logging.Formatter(
            "%(levelname)s %(asctime)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = setup_logging()

