import argparse

from telegram.ext import ApplicationBuilder

from src.helpers import config, log
from src.handlers import register_handlers


# Main
def main(debug: bool = False):
    """
    Revirathya - Telegram Bot

    Main function to start and configure Revirathya chatbot (@revirathya_bot).
    Application using Pooling system and depends on other API services:
        - Revirathya - API (Finance)
    
    The Chatbot are design to handle multiple type of conversation (and sub conversation).
    Mostly implement using CallbackQuery (or InlineQuery) pattern to minimize too many chat history.

    :params
        mode [str]: Set TRUE to run application on Debug mode. 
    """

    # Setup
    C = config.Config()
    logger = log.get_logger(debug)

    app = ApplicationBuilder().token(C.BOT_API_TOKEN.get_secret_value()).build()
    
    # Register Handler
    register_handlers(app, C, logger)

    # Run
    app.run_polling()


def get_args() -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", dest="debug")
    
    args = vars(parser.parse_args())
    return args


if __name__ == "__main__":
    args = get_args()
    main(debug = args["debug"])
