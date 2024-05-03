from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    API_TOKEN: SecretStr = Field(alias="API_TOKEN")
    TIMEZONE: str = Field(alias="TIMEZONE")

CONFIG = Config()
