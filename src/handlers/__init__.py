import pytz

from telegram.ext import Application

from src.handlers.finance.conversation import FinanceConversation
from src.helpers.bot import BotReplyMarkupHelper
from src.modules.bootstrap import Usecase


# Bootstraping
class Conversation:
    __finance_conv: FinanceConversation

    def __init__(self, reply_h: BotReplyMarkupHelper, tz: pytz.timezone, usecase: Usecase):
        self.__finance_conv = FinanceConversation(reply_h, tz, usecase)
    

    def register(self, app: Application):
        app.add_handler(self.__finance_conv.get_conversation())


# Register
def register_conversation(app: Application, usecase: Usecase):
    tz = pytz.timezone("Asia/Jakarta")
    reply_h = BotReplyMarkupHelper()

    conversation = Conversation(reply_h, tz, usecase)
    conversation.register(app)
