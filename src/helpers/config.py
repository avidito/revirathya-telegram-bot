from typing import Optional
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    BOT_API_TOKEN: SecretStr = Field(alias="BOT_API_TOKEN")
    FIN_API_HOSTNAME: str = Field(alias="FIN_API_HOSTNAME")
    FIN_API_PORT: Optional[int] = Field(alias="FIN_API_PORT", default=None)
