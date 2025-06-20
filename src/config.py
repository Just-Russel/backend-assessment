from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App metadata
    app_name: str = "Russel Library API"
    app_description: str = "An API for managing a library of books and authors"

    # Environment & versioning
    version: str = "v1.0.0"

    # Networking & security
    host: str = "0.0.0.0"
    port: int = 8000
    cors_allowed_origins: list[str] = ["*"]

    # Database
    db_uri: str = "./db.sqlite"

    # Debugging
    debug: bool = False


_settings = Settings()


def settings() -> Settings:
    return _settings
