import os
from logging import Logger

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import CallbackQueryHandler, CommandHandler, ConversationHandler, ContextTypes

from src.helpers.bot import BotReplyHelper
from src.domain import budget, expense
from src.handlers.finance import groups


class FinanceGroups:
    """
    Finance - Groups

    Group implementation of Finance conversation.
    """
    exp: groups.FinanceExpenseConversation

    def __init__(
        self,
        reply_h: BotReplyHelper,
        bud_usecase: budget.BudgetUsecase,
        exp_usecase: expense.ExpenseUsecase,
    ):
        self.exp = groups.FinanceExpenseConversation(reply_h, bud_usecase, exp_usecase)


class FinanceConversation:
    """
    Finance - Main Conversation

    Entry for Finance management conversation. 
    """
    # Constant
    TEMPLATE_DIR: str = os.path.join(os.path.dirname(__file__), "templates")
    STATES: dict = {
        state: i
        for i, state in enumerate([
            "INPUT_GROUP",
        ])
    }

    # Parameters
    __reply_h: BotReplyHelper
    __groups: FinanceGroups

    def __init__(
        self,
        reply_h: BotReplyHelper,
        bud_usecase: budget.BudgetUsecase,
        exp_usecase: expense.ExpenseUsecase,
        logger: Logger,
    ):
        self.__reply_h = reply_h
        self.__groups = FinanceGroups(reply_h, bud_usecase, exp_usecase)
        self.__logger = logger
    

    # Public
    def get_conversation(self) -> ConversationHandler:
        """Generate Finance Conversation"""
        # Initiate Conversation
        conv_handler = ConversationHandler(
            entry_points = [
                CommandHandler("finance", self.__entry_point_command),
            ],
            states = {
                self.STATES["INPUT_GROUP"]: [
                    self.__groups.exp.get_conversation(
                        entry_pattern = "^category=expense$",
                        return_state = ConversationHandler.END,
                        back_state = self.STATES["INPUT_GROUP"],
                        back_handler = self.__entry_point_callback,
                    ),
                    CallbackQueryHandler(self.__cancel, pattern="^cancel$"),
                ]
            },
            fallbacks = [
                CommandHandler("cancel", self.__fallback),
            ]
        )
        return conv_handler
    

    # Private
    def __base_entry_point(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> dict:
        # Initiate Object
        context.user_data["activity"] = "finance"

        # Set Reply Params
        text = self.__reply_h.render_template(self.TEMPLATE_DIR, "entry_point")
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Group: Expense", callback_data = "category=expense")],
            [InlineKeyboardButton("Cancel", callback_data = "cancel")],
        ])
        reply_params = {
            "text": text,
            "parse_mode": ParseMode.HTML,
            "reply_markup": reply_markup,
        }
        return reply_params

    async def __entry_point_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Setup and Change Reply
        reply_params = self.__base_entry_point(update, context)
        await update.message.reply_text(**reply_params)

        # Change State
        return self.STATES["INPUT_GROUP"]
    
    async def __entry_point_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Answer Query
        query = update.callback_query
        await query.answer()

        # Setup and Change Reply
        reply_params = self.__base_entry_point(update, context)
        await query.edit_message_text(**reply_params)

        # Change State
        return self.STATES["INPUT_GROUP"]
    
    async def __cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Answer Callback
        query = update.callback_query
        await query.answer()

        # Send Reply
        text = self.__reply_h.render_template(self.TEMPLATE_DIR, "fallback")
        await query.edit_message_text(
            text = text,
            parse_mode = ParseMode.HTML,
        )

        # Change State
        return ConversationHandler.END
        
    async def __fallback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Send Reply
        text = self.__reply_h.render_template(self.TEMPLATE_DIR, "fallback")
        await update.message.reply_text(
            text = text,
            parse_mode = ParseMode.HTML,
        )

        # Change State
        return ConversationHandler.END
