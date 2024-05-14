import os
from typing import Optional
from jinja2 import Template

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
