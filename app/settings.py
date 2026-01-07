from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    LOGFIRE_TOKEN: str
    DATABASE_LOWER_LIMIT: int = 1
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra='ignore'
    )


settings = Settings()
