from typing import Optional
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """
    Config

    Based on Pydantic Settings BaseSettings object.
    Directly read from ENV variables (rec: use Docker for easier env configuration).
    """
    
    BOT_API_TOKEN: SecretStr = Field(alias="BOT_API_TOKEN")
    FIN_API_HOSTNAME: str = Field(alias="FIN_API_HOSTNAME")
    FIN_API_PORT: Optional[int] = Field(alias="FIN_API_PORT", default=None)
