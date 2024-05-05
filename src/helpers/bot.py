import os
from typing import Optional
from jinja2 import Template


class BotReplyMarkupHelper:

    def render_text(self, template_dir: str, template_name: str, params: Optional[dict] = None) -> str:
        template_path = os.path.join(template_dir, f"{template_name}.html")
        with open(template_path, "r") as file:
            template = Template(file.read())
        
        rendered = template.render(**params) if (params) else template.render({})
        return rendered
