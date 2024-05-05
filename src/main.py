from telegram.ext import (
    Application,
    ApplicationBuilder,
)

from src.helpers.config import Config
from src.helpers.log import get_logger
from src.handlers import register_conversation
from src.modules import bootstrap_modules


# Main
def get_app(token: str) -> Application:
    app = ApplicationBuilder().token(token).build()
    return app


if __name__ == "__main__":
    # Init
    C = Config()
    logger = get_logger()

    # Setup
    app = get_app(token=C.BOT_API_TOKEN.get_secret_value())
    usecase = bootstrap_modules(C=C)

    register_conversation(app, usecase)

    # Run
    app.run_polling()