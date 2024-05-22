import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    CommandHandler,
)

from src.helpers.bot import BotReplyHelper
from src.domain import (
    budget,
    expense,
)
from src.handlers.finance.groups.expense.sub import (
    FinanceExpenseCreateConversation,
)


class FinanceExpenseSubConversation:
    """
    Finance - Expense Sub-Conversation

    Sub-Conversation implementation Finance Expense.
    """
    create_conv: FinanceExpenseCreateConversation

    def __init__(
        self,
        reply_h: BotReplyHelper,
        bud_usecase: budget.BudgetUsecase,
        exp_usecase: expense.ExpenseUsecase,
        template_dir: str
    ):
        self.create_conv = FinanceExpenseCreateConversation(reply_h, bud_usecase, exp_usecase, template_dir)


class FinanceExpenseConversation:
    """
    Finance - Expense Conversation

    Entry for Finance Expense management conversation.
    """
    # Constant
    TEMPLATE_DIR: str = os.path.join(os.path.dirname(__file__), "templates")
    STATES: dict = {
        state: i
        for i, state in enumerate([
            "INPUT_SUB",
            "END_GROUP",
            "BACK",
        ])
    }

    # Parameters
    __reply_h: BotReplyHelper
    __sub: FinanceExpenseSubConversation
    
    def __init__(
        self,
        reply_h: BotReplyHelper,
        bud_usecase: budget.BudgetUsecase,
        exp_usecase: expense.ExpenseUsecase,
    ):
        self.__reply_h = reply_h
        self.__sub = FinanceExpenseSubConversation(reply_h, bud_usecase, exp_usecase, self.TEMPLATE_DIR)
    

    # Public
    def get_conversation(
        self,
        entry_pattern: str,
        return_state: int,
        back_state: int,
        back_handler: CallbackQueryHandler,
    ) -> ConversationHandler:
        """Generate Finance Expense Conversation"""

        # Initiate Conversation
        conv_handler = ConversationHandler(
            entry_points = [
                CallbackQueryHandler(self.__entry_point, pattern = entry_pattern),
            ],
            states = {
                self.STATES["INPUT_SUB"]: [
                    self.__sub.create_conv.get_conversation(
                        entry_pattern = "^sub=create$",
                        return_state = self.STATES["END_GROUP"],
                        back_state = self.STATES["INPUT_SUB"],
                        back_handler =self.__entry_point,
                    ),
                    CallbackQueryHandler(self.__cancel, pattern="^cancel$"),
                    CallbackQueryHandler(self.__reply_h.route_callback_changer(back_handler, self.STATES["BACK"]), pattern="^back$"),
                ],
            },
            fallbacks = [
                CommandHandler("cancel", self.__fallback),
            ],
            map_to_parent = {
                self.STATES["END_GROUP"]: return_state,
                self.STATES["BACK"]: back_state,
            }
        )
        return conv_handler

    
    # Private - Handler
    async def __entry_point(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Answer Callback
        query = update.callback_query
        await query.answer()

        # Initiate Object
        context.user_data["group"] = "expense"

        # Change Reply Text
        text = self.__reply_h.render_template(self.TEMPLATE_DIR, "expense_entry_point")
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Create New Expense", callback_data = "sub=create")],
            [
                InlineKeyboardButton("Cancel", callback_data = "cancel"),
                InlineKeyboardButton("Back", callback_data = "back")
            ]
        ])
        await query.edit_message_text(
            text = text,
            parse_mode = ParseMode.HTML,
            reply_markup = reply_markup,
        )

        # Change State
        return self.STATES["INPUT_SUB"]
    
    async def __cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Answer Callback
        query = update.callback_query
        await query.answer()

        # Change Reply Text
        text = self.__reply_h.render_template(self.TEMPLATE_DIR, "expense_fallback")
        await query.edit_message_text(
            text = text,
            parse_mode = ParseMode.HTML,
        )

        # Change State
        return self.STATES["END_GROUP"]

    async def __fallback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Send Reply
        text = self.__reply_h.render_template(self.TEMPLATE_DIR, "expense_fallback")
        await update.message.reply_text(
            text = text,
            parse_mode = ParseMode.HTML,
        )

        # Change State
        return self.STATES["END_GROUP"]
