import pytz

from telegram.ext import Application

from src.modules.finance.conversation import FinanceConversation
from src.helper.bot import BotReplyMarkupHelper


# Bootstraping
class Conversation:
    __finance_conv: FinanceConversation

    def __init__(self, reply_h: BotReplyMarkupHelper, tz: pytz.timezone):
        self.__finance_conv = FinanceConversation(reply_h, tz)
    

    def register(self, app: Application):
        self.__finance_conv.register_conversation(app)


# Register
def register_conversation(app: Application, tz_str: str):
    tz = pytz.timezone(tz_str)
    reply_h = BotReplyMarkupHelper()

    conversation = Conversation(reply_h, tz)
    conversation.register(app)
