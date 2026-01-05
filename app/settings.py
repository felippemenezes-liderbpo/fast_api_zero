from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
    )

    LOGFIRE_TOKEN: str = ''
    DATABASE_LOWER_LIMIT: int = 1
    DATABASE_URL: str = ''
