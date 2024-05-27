import logging
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning


def get_logger(debug: bool = False) -> logging.Logger:
    """
    Get Logger

    Create logger for system logging and remove CallbackQueryHandler warnings
    """
    # Setup
    logger = logging.getLogger("rvr-bot")

    c_handler = logging.StreamHandler()
    if (debug):
        logging.basicConfig(level=logging.DEBUG)
        c_handler.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
        c_handler.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)
    
    logger.addHandler(
        c_handler.setFormatter(
            fmt = logging.Formatter(
                fmt = "[%(asctime)s] %(name)s - %(levelname)s - %(message)s",
                datefmt = "%Y-%m-%d %H:%M:%S",
            )
        )
    )

    # Remove other Logger
    logging.getLogger("httpx").setLevel(logging.WARNING)
    filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

    return logger