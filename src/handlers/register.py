from logging import Logger

from telegram.ext import Application

from src.helpers import bot, config
from src.modules.bootstrap import bootstrap_modules
from src.handlers.finance import FinanceConversation


# Register
def register_handlers(app: Application, C: config.Config, logger: Logger):
    """
    Register Handlers

    Registering any handlers that want to be included in Telegram conversational Chatbot.
    The handlers not necessarily ConversationHandler, it can also registering other Handler (e.g., CommandHandler)
    """
    # Setup
    reply_h = bot.BotReplyHelper()
    usecase = bootstrap_modules(C)

    # Register Handler
    fin_conv = FinanceConversation(
        reply_h,
        usecase.budget_usecase,
        usecase.expense_usecase,
        logger,
    )

    app.add_handlers([
        fin_conv.get_conversation()
    ])
