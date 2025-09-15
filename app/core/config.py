import os
from typing import Literal
from dotenv import load_dotenv

from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

LOG_DEFAULT_FORMAT = "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"

class LoggingSettings(BaseModel):
    log_level: Literal[
        'debug',
        'info',
        'warning',
        'error',
        'critical',
    ] = 'info'
    log_format: str = LOG_DEFAULT_FORMAT

class APIKeys(BaseModel):
    wb_token: str
    gemini_token: str


class DataBaseSettings(BaseModel):
    user: str
    password: str
    host: str
    port: int
    db_name: str
    pool_pre_ping: bool

    @property
    def url(self):
        return  f'postgresql+psycopg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='APP__',
        env_nested_delimiter='__',
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra='ignore',
        populate_by_name=True
    )
    db: DataBaseSettings
    api_keys: APIKeys
    logging: LoggingSettings = LoggingSettings()


settings = Settings()
