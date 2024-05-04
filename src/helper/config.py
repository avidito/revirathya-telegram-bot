from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    BOT_API_TOKEN: SecretStr = Field(alias="BOT_API_TOKEN")

CONFIG = Config()
