import pytz
from datetime import datetime
from typing import Coroutine

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.helpers.bot import BotReplyHelper
from src.domain import (
    budget,
    expense,
)
from src.handlers.finance.groups.expense.schemas import ConversationExpenseCreate


class FinanceExpenseCreateConversation:
    """
    Finance - Expense (Create) Conversation

    Sub-Conversation for creating expense modules.
    """
    # Constant
    STATES: dict = {
        state: i
        for i, state in enumerate([
            "INPUT_DATE",
            "INPUT_BUDGET_GROUP",
            "INPUT_BUDGET_TYPE",
            "INPUT_DESCRIPTION",
            "INPUT_AMOUNT",
            "INPUT_CONFIRM",
            "END_SUB",
            "BACK",
        ])
    }

    # Parameters
    __reply_h: BotReplyHelper
    __bud_usecase: budget.BudgetUsecase
    __exp_usecase: expense.ExpenseUsecase
    __template_dir: str

    def __init__(
        self,
        reply_h: BotReplyHelper,
        bud_usecase: budget.BudgetUsecase,
        exp_usecase: expense.ExpenseUsecase,
        template_dir: str,
    ):
        self.__reply_h = reply_h
        self.__bud_usecase = bud_usecase
        self.__exp_usecase = exp_usecase
        self.__template_dir = template_dir
    

    # Public
    def get_conversation(
        self,
        entry_pattern: str,
        return_state: int,
        back_state: int,
        back_cour: Coroutine,
    ) -> ConversationHandler:
        """Generate Finance Expense Create Sub Conversation"""

        # Initiate Conversation
        conv_handler = ConversationHandler(
            entry_points = [
                CallbackQueryHandler(self.__entry_point, pattern = entry_pattern),
            ],
            states = {
                self.STATES["INPUT_DATE"]: [
                    CallbackQueryHandler(self.__input_budget_group, pattern = "^date="),
                    self.__reply_h.cal_c.create_conversation(pattern = "calendar", return_state = self.STATES["INPUT_DATE"]),
                    *self.__reply_h.create_back_flow(c_cour = self.__cancel, b_cour = back_cour, b_state = self.STATES["BACK"]),
                ],
                self.STATES["INPUT_BUDGET_GROUP"]: [
                    CallbackQueryHandler(self.__input_budget_type, pattern = "^budget-group="),
                    *self.__reply_h.create_back_flow(c_cour = self.__cancel, b_cour = self.__entry_point, b_state = self.STATES["INPUT_DATE"]),
                ],
                self.STATES["INPUT_BUDGET_TYPE"]: [
                    CallbackQueryHandler(self.__input_description, pattern = "^budget-type="),
                    *self.__reply_h.create_back_flow(c_cour = self.__cancel, b_cour = self.__input_budget_group, b_state = self.STATES["INPUT_BUDGET_GROUP"]),
                ],
                self.STATES["INPUT_DESCRIPTION"]: [
                    MessageHandler(filters.Regex(".*"), self.__input_amount_message),
                    CallbackQueryHandler(self.__input_amount_callback, pattern="^message="),
                    *self.__reply_h.create_back_flow(c_cour = self.__cancel, b_cour = self.__input_budget_type, b_state = self.STATES["INPUT_BUDGET_TYPE"]),
                ],
                self.STATES["INPUT_AMOUNT"]: [
                    CallbackQueryHandler(self.__input_confirm, pattern = "^amount="),
                    self.__reply_h.num_c.create_conversation(pattern = "numpad", return_state = self.STATES["INPUT_AMOUNT"]),
                    *self.__reply_h.create_back_flow(c_cour = self.__cancel, b_cour = self.__input_description, b_state = self.STATES["INPUT_DESCRIPTION"]),
                ],
                self.STATES["INPUT_CONFIRM"]: [
                    CallbackQueryHandler(self.__submit, pattern = "^confirm="),
                    *self.__reply_h.create_back_flow(c_cour = self.__cancel, b_cour = self.__input_amount_callback, b_state = self.STATES["INPUT_AMOUNT"]),
                ],
            },
            fallbacks = [
                CommandHandler("cancel", self.__fallback),
            ],
            map_to_parent = {
                self.STATES["END_SUB"]: return_state,
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
        for key in ("data", "chat_id", "message_id",):
            if key in context.user_data:
                del context.user_data[key]
        
        context.user_data["data"] = ConversationExpenseCreate()

        # Change Reply Text
        text = self.__reply_h.render_template(self.__template_dir, "expense_create_entry_point", {
            "query": "date"
        })
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Today", callback_data=f"date={datetime.now(pytz.timezone('Asia/Jakarta')).strftime('%Y-%m-%d')}")],
            [InlineKeyboardButton("Choose with Calendar", callback_data="calendar")],
            self.__reply_h.create_back_flow_keyboard_button(),
        ])
        await query.edit_message_text(
            text = text,
            parse_mode = ParseMode.HTML,
            reply_markup = reply_markup,
        )

        # Change State
        return self.STATES["INPUT_DATE"]
    
    async def __input_budget_group(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Answer Callback
        query = update.callback_query
        await query.answer()

        # Parse Callback
        expense_data: ConversationExpenseCreate = context.user_data["data"]
        
        if (query.data == "back"):
            # Back Flow
            _date = expense_data.date
            expense_data.budget_group = None
        else:
            # Forward Flow
            _date = query.data.split("=")[1]
        
        expense_data.date = _date
        context.user_data["data"] = expense_data

        # Change Reply Text
        budget_groups = await self.__bud_usecase.get_groups()
        
        text = self.__reply_h.render_template(self.__template_dir, "expense_create_input", {
            "message": expense_data.to_message(),
            "query": "budget group",
        })
        reply_markup = InlineKeyboardMarkup([
            *[
                [InlineKeyboardButton(bg.budget_group, callback_data = f"budget-group={bg.id};{bg.budget_group}")]
                for bg in budget_groups
            ],
            self.__reply_h.create_back_flow_keyboard_button(),
        ])
        await query.edit_message_text(
            text = text,
            parse_mode = ParseMode.HTML,
            reply_markup = reply_markup,
        )

        # Change State
        return self.STATES["INPUT_BUDGET_GROUP"]

    async def __input_budget_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Answer Callback
        query = update.callback_query
        await query.answer()

        # Parse Callback
        expense_data: ConversationExpenseCreate = context.user_data["data"]
        
        if (query.data == "back"):
            # Back Flow
            budget_group = expense_data.budget_group
            expense_data.budget_type = None
        else:
            # Forward Flow
            budget_group = query.data.split("=")[1]
        
        expense_data.budget_group = budget_group
        context.user_data["data"] = expense_data

        # Change Reply Text
        budget_types = await self.__bud_usecase.get_types_by_group(budget_group_id = expense_data.get_budget_group_id())
        
        text = self.__reply_h.render_template(self.__template_dir, "expense_create_input", {
            "message": expense_data.to_message(),
            "query": "budget type",
        })
        reply_markup = InlineKeyboardMarkup([
            *[
                [InlineKeyboardButton(bt.budget_type, callback_data = f"budget-type={bt.id};{bt.budget_type}")]
                for bt in budget_types
            ],
            self.__reply_h.create_back_flow_keyboard_button(),
        ])
        await query.edit_message_text(
            text = text,
            parse_mode = ParseMode.HTML,
            reply_markup = reply_markup,
        )

        # Change State
        return self.STATES["INPUT_BUDGET_TYPE"]
    
    async def __input_description(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Answer Callback
        query = update.callback_query
        await query.answer()

        # Parse Callback
        expense_data: ConversationExpenseCreate = context.user_data["data"]

        if (query.data == "back"):
            # Back Flow
            budget_type = expense_data.budget_type
            expense_data.description = None
        else:
            # Forward Flow
            budget_type = query.data.split("=")[1]

        expense_data.budget_type = budget_type
        context.user_data["data"] = expense_data

        # Change Reply Text
        text = self.__reply_h.render_template(self.__template_dir, "expense_create_input", {
            "message": expense_data.to_message(),
            "query": "description",
        })
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Skip Description (Empty)", callback_data="message=")],
            self.__reply_h.create_back_flow_keyboard_button(),
        ])
        await query.edit_message_text(
            text = text,
            parse_mode = ParseMode.HTML,
            reply_markup = reply_markup,
        )

        # Save Chat ID and Message ID for future edit
        context.user_data["chat_id"] = update.effective_chat.id
        context.user_data["message_id"] = query.message.message_id

        # Change State
        return self.STATES["INPUT_DESCRIPTION"]
    
    def __input_amount(self, update: Update, context: ContextTypes.DEFAULT_TYPE, description: str) -> int:
        # Set Reply Params
        expense_data: ConversationExpenseCreate = context.user_data["data"]
        expense_data.description = description
        context.user_data["data"] = expense_data
        
        text = self.__reply_h.render_template(self.__template_dir, "expense_create_input", {
            "message": expense_data.to_message(),
            "query": "amount",
        })
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Custom Amount", callback_data = "numpad")],
            self.__reply_h.create_back_flow_keyboard_button(),
        ])
        reply_params = {
            "text": text,
            "reply_markup": reply_markup,
            "parse_mode": ParseMode.HTML,
        }
        return reply_params

    async def __input_amount_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Get Message
        description = update.message.text    
        
        # Update User Data and Change Reply Text
        reply_params = self.__input_amount(update, context, description)
        await context.bot.edit_message_text(
            **reply_params,
            chat_id = context.user_data["chat_id"],
            message_id = context.user_data["message_id"],
        )

        # Change State
        return self.STATES["INPUT_AMOUNT"]

    async def __input_amount_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Answer Query
        query = update.callback_query
        query.answer()

        # Parse Callback
        expense_data: ConversationExpenseCreate = context.user_data["data"]

        if (query.data == "back"):
            # Back Flow
            description = expense_data.description
            expense_data.amount = None
        else:
            # Forward Flow
            description = query.data.split("=")[1]
        
        # Update User Data and Change Reply text
        reply_params = self.__input_amount(update, context, description)
        await query.edit_message_text(**reply_params)

        # Change State
        return self.STATES["INPUT_AMOUNT"]

    
    async def __input_confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Answer Callback
        query = update.callback_query
        await query.answer()

        # Parse Callback
        _, amount = query.data.split("=")
        expense_data: ConversationExpenseCreate = context.user_data["data"]
        expense_data.amount = int(amount)
        context.user_data["data"] = expense_data

        # Change Reply Text
        text = self.__reply_h.render_template(self.__template_dir, "expense_create_confirm", {
            "message": expense_data.to_message(),
            "confirm": None,
        })
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Submit", callback_data = f"confirm=yes")],
            self.__reply_h.create_back_flow_keyboard_button(),
        ])
        await query.edit_message_text(
            text = text,
            parse_mode = ParseMode.HTML,
            reply_markup = reply_markup,
        )

        # Save Chat ID and Message ID for future edit (Back flow)
        context.user_data["chat_id"] = update.effective_chat.id
        context.user_data["message_id"] = query.message.message_id

        # Change State
        return self.STATES["INPUT_CONFIRM"]
    
    async def __submit(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Answer Callback
        query = update.callback_query
        await query.answer()

        # Parse Callback
        _, confirm = query.data.split("=")
        expense_data: ConversationExpenseCreate = context.user_data["data"]

        # Create Data
        if (confirm == "yes"):
            expense_payload = expense.FactExpense(
                budget_type_id = expense_data.get_budget_type_id(),
                date = expense_data.date,
                description = expense_data.description,
                amount = expense_data.amount,
            )
            _ = await self.__exp_usecase.create(expense_payload)

        # Change Reply Text
        text = self.__reply_h.render_template(self.__template_dir, "expense_create_confirm", {
            "message": expense_data.to_message(),
            "confirm": confirm,
        })
        await query.edit_message_text(
            text = text,
            parse_mode = ParseMode.HTML,
        )

        # Change State
        return self.STATES["END_SUB"]
        
    async def __cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Answer Callback
        query = update.callback_query
        await query.answer()
        
        # Send Reply
        text = self.__reply_h.render_template(self.__template_dir, "expense_create_fallback")
        await query.edit_message_text(
            text = text,
            parse_mode = ParseMode.HTML,
        )

        # Change State
        return self.STATES["END_SUB"]
    
    async def __fallback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Send Reply
        text = self.__reply_h.render_template(self.__template_dir, "expense_create_fallback")
        await update.message.reply_text(
            text = text,
            parse_mode = ParseMode.HTML,
        )

        # Change State
        return self.STATES["END_SUB"]
    