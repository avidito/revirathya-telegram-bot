import logging
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning


def get_logger(debug: bool = False) -> logging.Logger:
    # Get/Create
    logger = logging.getLogger("rvr-bot")
    
    # Setup
    logger.setLevel(logging.DEBUG) if (debug) else logger.setLevel(logging.INFO)
    logger.addHandler(
        logging.StreamHandler().setFormatter(
            logging.Formatter(
                fmt = "[%(asctime)s] %(name)s - %(levelname)s - %(message)s",
                datefmt = "%Y-%m-%d %H:%M:%S",
            )
        )
    )

    # Remove other logger
    logging.getLogger("httpx").setLevel(logging.WARNING)
    filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

    return logger