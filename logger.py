# ==========================================================
# Custom Logger Configuration
# ==========================================================

import logging
from datetime import datetime
from paths import LOGS_DIR

def setup_logger(name: str = "aita_logger") -> logging.Logger:

    timestamp = datetime.now().strftime("%d-%m-%y_%H-%M-%S")
    log_file = LOGS_DIR / f"{timestamp}.txt"

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S"
    )

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info(f"Logger initialized at {log_file}")

    return logger