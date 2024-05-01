from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    API_TOKEN: SecretStr = Field(alias="API_TOKEN", default="5971347712:AAGlL6kAaobT42-vRr2fDoDVZZK_H9GFwiI")
    TIMEZONE: str = Field(alias="TIMEZONE", default="Asia/Jakarta")

CONFIG = Config()
