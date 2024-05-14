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
        c_handler.setLevel(logging.DEBUG)
    else:
        c_handler.setLevel(logging.INFO)
    
    c_format = logging.Formatter(
        fmt = "[%(asctime)s] %(name)s - %(levelname)s - %(message)s",
        datefmt = "%Y-%m-%d %H:%M:%S",
    )
    c_handler.setFormatter(c_format)
    
    logger.addHandler(c_handler)

    # Remove other Logger
    logging.getLogger("httpx").setLevel(logging.WARNING)
    filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

    return logger