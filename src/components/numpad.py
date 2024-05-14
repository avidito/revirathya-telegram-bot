from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)


class NumpadComponent:
    """
    Numpad Component

    Create calendar (and its ConversationHandler) for easier number or amount input based on InlineKeyboard.
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
        self.msg_opening = "Please insert number:"
        self.msg_confirm = "You select '{amount}'"
    

    def create_numpad(self, amount: int):
        """
        Create Numpad

        Function to Create Numpad InlineKeyboard instance.

        :param
            amount [int]: Current amount to be displayed.
        
        :return
            InlineKeyboardMarkup. Numpad in format of InlineKeyboard.
        """
        # Initialize Callback Factory
        c_factory = self.__create_callback

        # Create: Header
        amount_fmt = f"{amount:_}".replace("_", ".")
        header = [InlineKeyboardButton(amount_fmt, callback_data=c_factory(amount))]

        # Create: Body
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

        # Create: Footer
        footer = [
            InlineKeyboardButton(" ", callback_data=c_factory(amount)),
            InlineKeyboardButton("0", callback_data=c_factory(amount, addition=str(0), mode="add")),
            InlineKeyboardButton(" ", callback_data=c_factory(amount)),
            InlineKeyboardButton("OK", callback_data=c_factory(amount, mode="enter")),
        ]

        # Assemble
        numpad_component = InlineKeyboardMarkup([
            header,
            *body,
            footer
        ])
        return numpad_component
    

    def create_conversation(
        self,
        pattern: str,
        return_state: int,
        handler_type: str = "callback-query",
    ):
        """
        Create ConversationHandler for Interacting with Numpad

        Create set of Conversation callback and handler to package Numpad component as ready to use functionality.
        """
        # Setup Conversation
        entry_point = CallbackQueryHandler(self.__init_conv, pattern=pattern) if (handler_type == "callback-query") else None
        conv_handler = ConversationHandler(
            entry_points = [entry_point],
            states = {
                self.STATES["CONTROL"]: [
                    CallbackQueryHandler(self.__trigger_ignore, pattern="^numpad;ignore"),
                    CallbackQueryHandler(self.__trigger_edit, pattern="^numpad;(clear|clear-entry|add)"),
                    CallbackQueryHandler(self.__trigger_enter, pattern="^numpad;enter"),
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
        text = self.msg_opening
        reply_markup = self.create_numpad(amount = 0)
        await query.edit_message_text(
            text = text,
            parse_mode = ParseMode.HTML,
            reply_markup = reply_markup,
        )

        # Change State
        return self.STATES["CONTROL"]
    
    async def __trigger_ignore(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Answer Callback
        query = update.callback_query
        await query.answer()

        # Change State
        return self.STATES["CONTROL"]


    async def __trigger_edit(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        # Answer Callback
        query = update.callback_query
        await query.answer()

        # Parse Callback
        _, _, amount = query.data.split(";")
        __amount = int(amount)
        
        # Change Reply Text
        if (context.user_data["tmp_numpad"] != __amount):
            text = self.msg_opening
            
            context.user_data["tmp_numpad"] = __amount
            reply_markup = self.create_numpad(__amount)

            await query.edit_message_text(
                text = text,
                parse_mode = ParseMode.HTML,
                reply_markup = reply_markup,
            )

        # Change State
        return self.STATES["CONTROL"]
    

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
        text = self.msg_confirm.format(**text_params)
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("OK", callback_data=f"amount={amount}")]
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
            "Cancelling: Numpad input. See you later!"
        )

        return ConversationHandler.END

    