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
    PARENT_STATE: Optional[int]
    opening_message: str
    validation_message: str

    def __init__(self):
        self.CONTROL_STATE = None
        self.END_STATE = None
        self.PARENT_STATE = None
        self.opening_message = "Please select date:"
        self.validation_message = "You select '{date}'"


    def create_calendar(self, year: int, month: int):
        # Create Callback Factory
        c_factory = partial(self.__create_callback, year, month)

        # Header
        header = [InlineKeyboardButton(f"{calendar.month_name[month]} {year}", callback_data=c_factory(mode="ignore"))]

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

        # Footer
        footer = [
            InlineKeyboardButton("<", callback_data=c_factory(mode="prev")),
            InlineKeyboardButton(">", callback_data=c_factory(mode="next")),
        ]

        # Calendar
        calendar_component = InlineKeyboardMarkup([
            header,
            week_header,
            *week_body,
            footer,
        ])

        return calendar_component
    
    def create_conversation(
            self,
            pattern: str,
            control_state: int,
            end_state: int,
            parent_state: int,
            fallback_func: callable,
            handler_type: str = "callback-query"
        ) -> ConversationHandler:
        # Init State Params
        self.CONTROL_STATE = control_state
        self.END_STATE = end_state
        self.PARENT_STATE = parent_state

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
                CommandHandler("cancel", fallback_func)
            ],
            map_to_parent = {
                self.END_STATE: self.PARENT_STATE,
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
    

    # Private - Handler
    async def __init_conv(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        
        year, month = map(int, datetime.now().strftime("%Y-%m").split("-"))
        cal_keyboard = self.create_calendar(year, month)

        await query.answer()
        await query.edit_message_text(
            text=self.opening_message,
            parse_mode=ParseMode.HTML,
            reply_markup=cal_keyboard,
        )
        return self.CONTROL_STATE


    async def __trigger_ignore(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()

        return self.CONTROL_STATE


    async def __trigger_navigation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        _, _, year, month, _ = query.data.split(";")

        cal_keyboard = self.create_calendar(int(year), int(month))

        await query.answer()
        await query.edit_message_text(
            text=self.opening_message,
            parse_mode=ParseMode.HTML,
            reply_markup = cal_keyboard
        )
        
        return self.CONTROL_STATE


    async def __trigger_choose(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        _, _, year, month, day = query.data.split(";")

        calendar_date = f"{year}-{month:>02}-{day:>02}"
        context.user_data["calendar_date"] = calendar_date

        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Ok", callback_data=f"calendar-date={calendar_date}")]])

        await query.answer()
        await query.edit_message_text(
            text=self.validation_message.format(date=calendar_date),
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard
        )
        return self.END_STATE
