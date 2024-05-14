import calendar
from functools import partial
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)


class CalenderComponent:
    """
    Calendar Component

    Create calendar (and its ConversationHandler) for easier date input based on InlineKeyboard.
    The implementation are heavily inspired by: https://github.com/unmonoqueteclea/calendar-telegram

    :params
        return_state [int]: Return state after conversation end.
    """
    STATES: dict = {
        state: i
        for i, state in enumerate([
            "CONTROL",
            "CHOOSE",
        ])
    }
    msg_opening: str
    msg_confirm: str

    def __init__(self):
        self.msg_opening = "Please select date:"
        self.msg_confirm = "You select '{date}'"


    def create_calendar(self, year: int, month: int) -> InlineKeyboardMarkup:
        """
        Create Calendar

        Function to Create Calendar InlineKeyboard instance.

        :param
            year [int]: Year of calendar.
            month [int]: Month of calendar.
        
        :return
            InlineKeyboardMarkup. Calendar in format of InlineKeyboard.
        """
        # Initialize Callback Factory
        c_factory = partial(self.__create_callback, year, month)

        # Create: Header
        month_year_fmt = f"{calendar.month_name[month]} {year}"
        header = [InlineKeyboardButton(month_year_fmt, callback_data=c_factory(mode="ignore"))]

        # Create: Body
        week_header = [
            InlineKeyboardButton(btn, callback_data=c_factory(mode="ignore"))
            for btn in ("Mo", "Tu", "We", "Th", "Fr", "Sa", "Su",)
        ]
        week_body = [
            [
                InlineKeyboardButton(str(day), callback_data=c_factory(day, "choose"))
                if (day) else
                InlineKeyboardButton(" ", callback_data=c_factory(mode="ignore"))
                for day in week
            ]
            for week in calendar.monthcalendar(year, month)
        ]

        body = [week_header, *week_body]

        # Create: Footer
        footer = [
            InlineKeyboardButton("<", callback_data=c_factory(mode="prev")),
            InlineKeyboardButton(">", callback_data=c_factory(mode="next")),
        ]

        # Assemble
        calendar_component = InlineKeyboardMarkup([
            header,
            *body,
            footer,
        ])
        return calendar_component
    
    def create_conversation(
            self,
            pattern: str,
            return_state: int,
            handler_type: str = "callback-query",
        ) -> ConversationHandler:
        """
        Create ConversationHandler for Interacting with Calendar

        Create set of Conversation callback and handler to package Calendar component as ready to use functionality.
        """
        # Setup Conversation
        entry_point = CallbackQueryHandler(self.__init_conv, pattern=pattern) if (handler_type == "callback-query") else None
        conv_handler = ConversationHandler(
            entry_points = [entry_point],
            states = {
                self.STATES["CONTROL"]: [
                    CallbackQueryHandler(self.__trigger_ignore, pattern="^calendar;ignore"),
                    CallbackQueryHandler(self.__trigger_navigation, pattern="^calendar;(prev|next)"),
                    CallbackQueryHandler(self.__trigger_choose, pattern="^calendar;choose"),
                ]
            },
            fallbacks=[
                CommandHandler("cancel", self.__fallback),
            ],
            map_to_parent={
                self.STATES["CHOOSE"]: return_state,
            }
        )
        return conv_handler
    

    # Private
    def __create_callback(self, year: int, month: int, day: int = 0, mode: str = "ignore") -> str:
        prefix = "calendar"
        if (mode == "ignore"):
            callback_items = [prefix, mode, year, month, 0]
        elif (mode == "prev"):
            callback_items = [prefix, mode, year, month - 1, 0]if (month > 1) else [prefix, mode, year - 1, 12, 0] # Check if Prev from Jan (change year)
        elif (mode == "next"):
            callback_items = [prefix, mode, year, month + 1, 0] if (month < 12) else [prefix, mode, year + 1, 1, 0] # Check if Next from Dec (change year)
        elif (mode == "choose"):
            callback_items = [prefix, mode, year, month, day]
        
        return ";".join(map(str, callback_items))
    

    # Private - Handlers
    async def __init_conv(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Answer Query
        query = update.callback_query
        await query.answer()
        
        # Initiate Vars
        year, month = map(int, datetime.now().strftime("%Y-%m").split("-"))

        # Change Reply Text
        text = self.msg_opening
        reply_markup = self.create_calendar(year, month)
        await query.edit_message_text(
            text = text,
            parse_mode = ParseMode.HTML,
            reply_markup = reply_markup,
        )

        # Change State
        return self.STATES["CONTROL"]


    async def __trigger_ignore(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Answer Query
        query = update.callback_query
        await query.answer()

        # Change State
        return self.STATES["CONTROL"]


    async def __trigger_navigation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Answer Query
        query = update.callback_query
        await query.answer()
        
        # Parse Callback
        _, _, year, month, _ = query.data.split(";")

        # Change Reply Text
        text = self.msg_opening
        reply_markup = self.create_calendar(int(year), int(month))
        await query.edit_message_text(
            text = text,
            parse_mode = ParseMode.HTML,
            reply_markup = reply_markup,
        )
        
        # Change State
        return self.STATES["CONTROL"]


    async def __trigger_choose(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Answer Query
        query = update.callback_query
        await query.answer()
        
        # Parse Callback
        _, _, year, month, day = query.data.split(";")
        calendar_date = f"{year}-{month:>02}-{day:>02}"

        # Change Reply Text
        text_params = {
            "date": calendar_date
        }
        text = self.msg_confirm.format(**text_params)

        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Ok", callback_data=f"date={calendar_date}")]
        ])
        
        await query.edit_message_text(
            text = text,
            parse_mode = ParseMode.HTML,
            reply_markup = reply_markup,
        )

        # Change State
        return self.STATES["CHOOSE"]


    async def __fallback(self, update: Update, context: ContextTypes):
        """
        Cancel and End the Conversation
        """
        await update.message.reply_text(
            "Cancelling: Calendar input. See you later!"
        )

        return ConversationHandler.END