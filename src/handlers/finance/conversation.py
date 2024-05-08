import os
import pytz
from datetime import datetime

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.constants import ParseMode
from telegram.ext import (
    CallbackQueryHandler,
    ConversationHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from src.components import calendar, numpad
from src.helpers.bot import BotReplyMarkupHelper
from src.modules.bootstrap import Usecase

from src.handlers.finance.schemas import (
    ExpenseCreate,
)


# Conversation
class FinanceConversation:
    __reply_h: BotReplyMarkupHelper
    __tz: pytz.timezone
    __usecase: Usecase

    __calendar_c: calendar.CalenderComponent
    __numpad_c: numpad.NumpadComponent
    __template_dir: str

    # Constant
    STATES = {
        state: i
        for i, state in enumerate([
            "INPUT_ACTION",
            "INPUT_DATE",
            "INPUT_BUDGET_GROUP",
            "INPUT_BUDGET_TYPE",
            "INPUT_DESCRIPTION",
            "INPUT_AMOUNT",
            "INPUT_CONFIRMATION",
            "CALENDAR_CONTROL",
            "CALENDAR_END_CONTROL",
            "NUMPAD_CONTROL",
            "NUMPAD_END_CONTROL",
        ])
    }

    def __init__(self, reply_h: BotReplyMarkupHelper, tz: pytz.timezone, usecase: Usecase):
        self.__reply_h = reply_h
        self.__tz = tz
        self.__usecase = usecase

        self.__calendar_c = calendar.CalenderComponent()
        self.__numpad_c = numpad.NumpadComponent()
        self.__template_dir = os.path.join(os.path.dirname(__file__), "templates")
    

    def get_conversation(self) -> ConversationHandler:
        # Define Flow
        conv_handler = ConversationHandler(
            entry_points = [
                CommandHandler("finance", self.__start),
            ],
            states={
                self.STATES["INPUT_ACTION"]: [
                    CallbackQueryHandler(self.__input_date)
                ],
                self.STATES["INPUT_DATE"]: [
                    CallbackQueryHandler(self.__input_budget_group, pattern = "^calendar-date="),
                    self.__calendar_c.create_conversation(
                        pattern = "gen-calendar",
                        control_state = self.STATES["CALENDAR_CONTROL"],
                        end_state = self.STATES["CALENDAR_END_CONTROL"],
                        after_conv_state = self.STATES["INPUT_DATE"],
                        fallback_func = self.cancel,
                    )
                ],
                self.STATES["INPUT_BUDGET_GROUP"]: [
                    CallbackQueryHandler(self.__input_budget_type, pattern = "^budget-group=")
                ],
                self.STATES["INPUT_BUDGET_TYPE"]: [
                    CallbackQueryHandler(self.__input_description, pattern = "^budget-type=")
                ],
                self.STATES["INPUT_DESCRIPTION"]: [
                    MessageHandler(filters.Regex(".*"), self.__input_amount)
                ],
                self.STATES["INPUT_AMOUNT"]: [
                    CallbackQueryHandler(self.__input_confirmation, pattern = "^numpad-amount="),
                    self.__numpad_c.create_conversation(
                        pattern = "gen-numpad",
                        control_state = self.STATES["NUMPAD_CONTROL"],
                        end_state = self.STATES["NUMPAD_END_CONTROL"],
                        after_conv_state = self.STATES["INPUT_AMOUNT"],
                        fallback_func = self.cancel,
                    )
                ],
                self.STATES["INPUT_CONFIRMATION"]: [
                    CallbackQueryHandler(self.__echo, pattern = "^confirm=")
                ],
            },
            fallbacks=[
                CommandHandler("cancel", self.cancel)
            ]
        )
        return conv_handler


    # Handler
    async def __start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Starting Finance conversation
        """
        # Initiate Object
        if "data" in context.user_data:
            del context.user_data["data"]
        context.user_data["data"] = ExpenseCreate()
        
        # Reply Chat
        text = self.__reply_h.render_text(self.__template_dir, "init_conv")
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Create", callback_data = "command=create")],
        ])
        await update.message.reply_text(
            text = text,
            parse_mode = ParseMode.HTML,
            reply_markup = reply_markup,
        )

        # Change State
        return self.STATES["INPUT_ACTION"]


    async def __input_date(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Answer Callback
        query = update.callback_query
        await query.answer()
        
        # Parse Callback
        _, command = query.data.split("=")
        context.user_data["command"] = command

        # Change Reply Text
        text_params = {"params": "date"}
        text = self.__reply_h.render_text(self.__template_dir, "create_input_query_conv", text_params)
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Today", callback_data = f"calendar-date={datetime.now(self.__tz).strftime('%Y-%m-%d')}")],
            [InlineKeyboardButton("Choose Date", callback_data = f"gen-calendar")]
        ])
        await query.edit_message_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )

        # Change State
        return self.STATES["INPUT_DATE"]


    async def __input_budget_group(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Answer Callback
        query = update.callback_query
        await query.answer()

        # Parse Callback
        _, _date = query.data.split("=")
        expense_data: ExpenseCreate = context.user_data["data"]
        expense_data.date = _date
        context.user_data["data"] = expense_data

        # Change Reply Text
        text_params = {
            "data": expense_data.to_message(),
            "params": "budget group"
        }
        text = self.__reply_h.render_text(self.__template_dir, "create_input_query_conv", text_params)
        
        budget_groups = await self.__usecase.budget_usecase.get_groups()
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(bg.budget_group, callback_data = f"budget-group={bg.id};{bg.budget_group}")]
            for bg in budget_groups
        ])

        await query.edit_message_text(
            text = text,
            parse_mode = ParseMode.HTML,
            reply_markup = reply_markup
        )

        # Change State
        return self.STATES["INPUT_BUDGET_GROUP"]
    

    async def __input_budget_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Answer Callback
        query = update.callback_query
        await query.answer()
        
        # Parse Callback
        _, budget_groups = query.data.split("=")
        expense_data: ExpenseCreate = context.user_data["data"]
        expense_data.budget_group = budget_groups
        context.user_data["data"] = expense_data
               
        # Change Reply Text
        text_params = {
            "data": expense_data.to_message(),
            "params": "budget type"
        }
        text = self.__reply_h.render_text(self.__template_dir, "create_input_query_conv", text_params)

        budget_types = await self.__usecase.budget_usecase.get_types_by_group(budget_group_id = expense_data.get_budget_group_id())
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(bt.budget_type, callback_data = f"budget-type={bt.id};{bt.budget_type}")]
            for bt in budget_types
        ])

        await query.edit_message_text(
            text = text,
            parse_mode = ParseMode.HTML,
            reply_markup = reply_markup
        )

        return self.STATES["INPUT_BUDGET_TYPE"]


    async def __input_description(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Answer Callback
        query = update.callback_query
        await query.answer()
        
        # Parse Callback
        _, budget_type = query.data.split("=")
        expense_data: ExpenseCreate = context.user_data["data"]
        expense_data.budget_type = budget_type
        context.user_data["data"] = expense_data

        # Change Reply Text
        text_params = {
            "data": expense_data.to_message(),
            "params": "description"
        }
        text = self.__reply_h.render_text(self.__template_dir, "create_input_query_conv", text_params)

        await query.edit_message_text(
            text = text,
            parse_mode = ParseMode.HTML,
        )

        # Save Chat ID and Message ID for future edit
        context.user_data["chat_id"] = update.effective_chat.id
        context.user_data["last_message_id"] = query.message.message_id

        # Change State
        return self.STATES["INPUT_DESCRIPTION"]
    

    async def __input_amount(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Get Message
        description = update.message.text
        expense_data: ExpenseCreate = context.user_data["data"]
        expense_data.description = description
        context.user_data["data"] = expense_data

        # Edit Reply Text
        text_params = {
            "data": expense_data.to_message(),
            "params": "amount"
        }
        text = self.__reply_h.render_text(self.__template_dir, "create_input_query_conv", text_params)

        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Custom Amount", callback_data = f"gen-numpad")],
        ])

        await context.bot.edit_message_text(
            text = text,
            parse_mode = ParseMode.HTML,
            reply_markup = reply_markup,
            chat_id = context.user_data["chat_id"],
            message_id = context.user_data["last_message_id"],
        )

        # Change State  
        return self.STATES["INPUT_AMOUNT"]
    

    async def __input_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Answer Callback
        query = update.callback_query
        await query.answer()

        # Parse Callback
        _, amount = query.data.split("=")
        expense_data: ExpenseCreate = context.user_data["data"]
        expense_data.amount = amount
        context.user_data["data"] = expense_data
        
        # Edit Reply Text
        text_params = {
            "data": expense_data.to_message(),
        }
        text = self.__reply_h.render_text(self.__template_dir, "create_input_confirm_conv", text_params)

        reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Yes", callback_data=f"confirm=yes"),
                InlineKeyboardButton("No", callback_data=f"confirm=no")
            ]
        ])

        await query.edit_message_text(
            text = text,
            parse_mode = ParseMode.HTML,
            reply_markup = reply_markup,
        )

        # Change State
        return self.STATES["INPUT_CONFIRMATION"]
    

    async def __echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Answer Callback
        query = update.callback_query
        await query.answer()
        
        # Parse Callback
        _, confirm = query.data.split("=")
        context.user_data["confirm"] = confirm
        expense_data: ExpenseCreate = context.user_data["data"]

        # Edit Reply Text
        text_params = {
            "data": expense_data.to_message(),
            "confirm": confirm,
        }
        text = self.__reply_h.render_text(self.__template_dir, "create_input_confirm_conv", text_params)
        
        await query.edit_message_text(
            text = text,
            parse_mode = ParseMode.HTML,
        )

        # Change State
        del context.user_data["data"]
        del context.user_data["confirm"]
        return ConversationHandler.END


    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancels and ends the conversation."""
        user = update.message.from_user
        await update.message.reply_text(
            "Bye! I hope we can talk again some day."
        )

        return ConversationHandler.END
