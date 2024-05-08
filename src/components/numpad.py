from typing import Optional

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


class NumpadComponent:
    CONTROL_STATE: Optional[int]
    END_STATE: Optional[int]
    PARENT_STATE: Optional[int]
    opening_message: str
    validation_message: str

    def __init__(self):
        self.CONTROL_STATE = None
        self.END_STATE = None
        self.PARENT_STATE = None
        self.opening_message = "Please insert number:"
        self.validation_message = "You select '{amount}'"
    

    def create_numpad(self, amount: int):
        # Create Callback Factory
        c_factory = self.__create_callback

        # Header
        amount_fmt = f"{amount:_}".replace("_", ".")
        header = [InlineKeyboardButton(amount_fmt, callback_data=c_factory(amount))]

        # Body
        numpad_body = [
            [
                InlineKeyboardButton(str(d), callback_data=c_factory(amount, addition=str(d), mode="add"))
                for d in range(i, i+3)
            ]
            for i in range(1, 9, 3)
        ]
        side_operator = [
            [InlineKeyboardButton("C", callback_data=c_factory(amount, mode="clear"))],
            [InlineKeyboardButton("CE", callback_data=c_factory(amount, mode="clear-entry"))],
            [InlineKeyboardButton("000", callback_data=c_factory(amount, addition="000", mode="add"))],
        ]

        body = [
            r + s
            for r, s in zip(numpad_body, side_operator)
        ]

        # Footer
        footer = [
            InlineKeyboardButton(" ", callback_data=c_factory(amount)),
            InlineKeyboardButton("0", callback_data=c_factory(amount, addition=str(0), mode="add")),
            InlineKeyboardButton(" ", callback_data=c_factory(amount)),
            InlineKeyboardButton("OK", callback_data=c_factory(amount, mode="enter")),
        ]

        # Numpad
        numpad_component = InlineKeyboardMarkup([
            header,
            *body,
            footer
        ])
        return numpad_component
    

    def create_conversation(
        self,
        pattern: str,
        control_state: int,
        end_state: int,
        after_conv_state: int,
        fallback_func: callable,
        handler_type: str = "callback-query",
    ):
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
                    CallbackQueryHandler(self.__trigger_ignore, pattern="^numpad;ignore"),
                    CallbackQueryHandler(self.__trigger_edit, pattern="^numpad;(clear|clear-entry|add)"),
                    CallbackQueryHandler(self.__trigger_enter, pattern="^numpad;enter"),
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
    def __create_callback(self, amount: int, addition: Optional[str] = None, mode: str = "ignore") -> str:
        prefix = "numpad"
        if (mode == "ignore"):
            callback_items = [prefix, mode, amount]
        elif (mode == "clear"):
            callback_items = [prefix, mode, 0]
        elif (mode == "clear-entry"):
            callback_items = [prefix, mode, self.__remove_digit(amount)]
        elif (mode == "add"):
            callback_items = [prefix, mode, self.__add_digit(amount, addition)]
        elif (mode == "enter"):
            callback_items = [prefix, mode, amount]

        return ";".join(map(str, callback_items))

    def __remove_digit(self, amount: int) -> int:
        return amount // 10

    def __add_digit(self, amount: int, addition: str) -> int:
        if (addition == "000"):
            return amount * 1000 if (amount > 0) else 0
        else:
            return (amount * 10) + int(addition)
    

    # Private - Handlers
    async def __init_conv(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Answer Callback
        query = update.callback_query
        await query.answer()
        
        # Initiate Vars
        context.user_data["tmp_numpad"] = 0

        # Change Reply Text
        text = self.opening_message
        reply_markup = self.create_numpad(amount = 0)
        await query.edit_message_text(
            text = text,
            parse_mode = ParseMode.HTML,
            reply_markup = reply_markup,
        )

        # Change State
        return self.CONTROL_STATE
    
    async def __trigger_ignore(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Answer Callback
        query = update.callback_query
        await query.answer()

        # Change State
        return self.CONTROL_STATE


    async def __trigger_edit(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Answer Callback
        query = update.callback_query
        await query.answer()

        # Parse Callback
        _, _, amount = query.data.split(";")
        __amount = int(amount)
        
        # Change Reply Text
        if (context.user_data["tmp_numpad"] != __amount):
            text = self.opening_message
            
            context.user_data["tmp_numpad"] = __amount
            reply_markup = self.create_numpad(__amount)

            await query.edit_message_text(
                text = text,
                parse_mode = ParseMode.HTML,
                reply_markup = reply_markup,
            )

        # Change State
        return self.CONTROL_STATE
    

    async def __trigger_enter(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Answer Callback
        query = update.callback_query
        await query.answer()
        del context.user_data["tmp_numpad"]

        # Parse Callback
        _, _, amount = query.data.split(";")

        # Edit Keyboard
        text_params = {
            "amount": f"{int(amount):_}".replace("_", ".")
        }
        text = self.validation_message.format(**text_params)
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Ok", callback_data=f"numpad-amount={amount}")]
        ])

        await query.edit_message_text(
            text = text,
            parse_mode = ParseMode.HTML,
            reply_markup = reply_markup,
        )

        # Change State
        return self.END_STATE

    