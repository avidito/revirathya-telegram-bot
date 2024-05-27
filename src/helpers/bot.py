import os
from jinja2 import Template
from typing import Coroutine, List, Optional, Tuple

from telegram import InlineKeyboardButton
from telegram.ext import CallbackQueryHandler

from src.components import calendar, numpad


class BotReplyHelper:
    """
    Bot Reply Helper

    Helper class to make reply formatting and custom component interaction easier.
    New component must be register manually on this class so it can be used on conversation.
    Register Component handler/factory on __init__ function.
    """
    cal_c: calendar.CalenderComponent
    num_c: numpad.NumpadComponent

    def __init__(self):
        self.cal_c = calendar.CalenderComponent()
        self.num_c = numpad.NumpadComponent()
    

    # Public
    def render_template(self, template_dir: str, template_name: str, params: Optional[dict] = None) -> str:
        """
        Render Text from Template

        Text will be rendered via Jinja templating.

        :params
            template_dir [str]: Path to template directory.
            template_name [str]: Template filename (without extension).
            params [Optional[dict]]: Parameters that need to be injected to template (default=None).
        
        :return
            str. Formatted templates on string format.
        """
        # Get Template
        template_path = os.path.join(template_dir, f"{template_name}.html")
        with open(template_path, "r") as file:
            template = Template(file.read())
        
        # Render Template
        rendered = template.render(**params) if (params) else template.render({})
        return rendered
    
    def create_back_flow(
        self,
        c_cour: Coroutine,
        b_cour: Coroutine,
        b_state: int,
        c_pattern: str = "^cancel$",
        b_pattern: str = "^back$",
    ) -> Tuple[CallbackQueryHandler, CallbackQueryHandler]:
        """
        Create Callback Handler for Cancel and Back (Return).

        Create CallbackQueryHandler for Cancel and Back logic in conversation.

        :params
            c_cour [Coroutine]: Function (async) for Cancel conversation.
            b_cour [Coroutine]: Function (async) for Back (Return) conversation.
            b_state [int]: Back state for Back Handler.
            c_pattern [str]: (default: "^cancel$") Pattern for Cancel.
            b_pattern [str]: (default: "^back$") Pattern for Back (Return).
        
        :return
            Tuple[CallbackQueryHandler, CallbackQueryHandler]. Handler for Cancel and Back (Return) logic.
        """
        c_handler = CallbackQueryHandler(c_cour, pattern = c_pattern)
        b_handler = CallbackQueryHandler(self.route_callback_changer(b_cour, b_state), pattern = b_pattern)
        return (c_handler, b_handler)

    def create_back_flow_keyboard_button(self, c_pattern: str = "cancel", b_pattern: str = "back") -> List[InlineKeyboardButton]:
        """
        Create InlineKeyboardButton set for Back Flow

        Create simple keyboards button for Cancel and Back (Return) logic.

        :params
            c_pattern [str]: (default: "cancel") Pattern for Cancel.
            b_pattern [str]: (default: "back") Pattern for Back (Return).
        
        :return
            List[InlineKeyboardButton]. Keyboards button for Back Flow.
        """
        return [
            InlineKeyboardButton("Cancel", callback_data = c_pattern),
            InlineKeyboardButton("Back", callback_data = b_pattern),
        ]

    
    def route_callback_changer(self, handler: Coroutine, target: int) -> Coroutine:
        """
        Change Callback Handler Conversation Route

        Change the target state of defined Callback Query Handler.

        :params
            handler [CallbackQueryHandler]: Handler that want to be re-route.
            target [int]: New target state for handler.
        
        :return
            CallbackQueryHandler. Re-route handler.
        """
        async def wrapper(*args, **kwargs):
            _ = await handler(*args, **kwargs)
            return target
        
        return wrapper