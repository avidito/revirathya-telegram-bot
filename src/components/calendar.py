import calendar
from typing import Optional
from datetime import datetime
from functools import partial

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.constants import ParseMode
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)


class CalenderComponent:
    CONTROL_STATE: Optional[int]
    END_STATE: Optional[int]
    AFTER_CONV_STATE: Optional[int]
    opening_message: str
    validation_message: str

    def __init__(self):
        self.CONTROL_STATE = None
        self.END_STATE = None
        self.AFTER_CONV_STATE = None
        self.opening_message = "Please select date:"
        self.validation_message = "You select '{date}'"


    def create_calendar(self, year: int, month: int):
        # Create Callback Factory
        c_factory = partial(self.__create_callback, year, month)

        # Header
        month_year_fmt = f"{calendar.month_name[month]} {year}"
        header = [InlineKeyboardButton(month_year_fmt, callback_data=c_factory(mode="ignore"))]

        # Body
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

        # Footer
        footer = [
            InlineKeyboardButton("<", callback_data=c_factory(mode="prev")),
            InlineKeyboardButton(">", callback_data=c_factory(mode="next")),
        ]

        # Calendar
        calendar_component = InlineKeyboardMarkup([
            header,
            *body,
            footer,
        ])

        return calendar_component
    
    def create_conversation(
            self,
            pattern: str,
            control_state: int,
            end_state: int,
            after_conv_state: int,
            fallback_func: callable,
            handler_type: str = "callback-query",
        ) -> ConversationHandler:
        # Init State Params
        self.CONTROL_STATE = control_state
        self.END_STATE = end_state
        self.AFTER_CONV_STATE = after_conv_state

        # Init Conversation
        entry_point = CallbackQueryHandler(self.__init_conv, pattern=pattern) if (handler_type == "callback-query") else None
        conv_handler = ConversationHandler(
            entry_points=[entry_point],
            states={
                self.CONTROL_STATE: [
                    CallbackQueryHandler(self.__trigger_ignore, pattern="^calendar;ignore"),
                    CallbackQueryHandler(self.__trigger_navigation, pattern="^calendar;(prev|next)"),
                    CallbackQueryHandler(self.__trigger_choose, pattern="^calendar;choose"),
                ]
            },
            fallbacks=[
                CommandHandler("cancel", fallback_func),
            ],
            map_to_parent={
                self.END_STATE: self.AFTER_CONV_STATE,
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
        text = self.opening_message
        reply_markup = self.create_calendar(year, month)
        await query.edit_message_text(
            text = text,
            parse_mode = ParseMode.HTML,
            reply_markup = reply_markup,
        )

        # Change State
        return self.CONTROL_STATE


    async def __trigger_ignore(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Answer Query
        query = update.callback_query
        await query.answer()

        # Change State
        return self.CONTROL_STATE


    async def __trigger_navigation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Answer Query
        query = update.callback_query
        await query.answer()
        
        # Parse Callback
        _, _, year, month, _ = query.data.split(";")

        # Change Reply Text
        text = self.opening_message
        reply_markup = self.create_calendar(int(year), int(month))
        await query.edit_message_text(
            text = text,
            parse_mode = ParseMode.HTML,
            reply_markup = reply_markup,
        )
        
        # Change State
        return self.CONTROL_STATE


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
        text = self.validation_message.format(**text_params)

        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Ok", callback_data=f"calendar-date={calendar_date}")]
        ])
        
        await query.edit_message_text(
            text = text,
            parse_mode = ParseMode.HTML,
            reply_markup = reply_markup,
        )

        # Change State
        return self.END_STATE
