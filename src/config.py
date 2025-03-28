import logging
from enum import StrEnum

from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import CONFIG_VAR_PREFIX


class Environment(StrEnum):
    development = "development"
    staging = "staging"
    production = "production"


api_host_map: dict[Environment, str] = {
    Environment.development: "localhost",
    Environment.staging: "api.staging.justrussel.com",
    Environment.production: "api.justrussel.com",
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix=CONFIG_VAR_PREFIX,
        case_sensitive=False,
        extra="ignore",
    )

    # App metadata
    app_name: str = "API template"
    app_description: str = "An API template"
    service_name: str = "api-template"

    # Environment & versioning
    version: str = "unknown"
    environment: Environment = Environment.development
    api_host: str = api_host_map[environment]
    auto_reload: bool = False

    # Networking & security
    host: str = "0.0.0.0"
    port: int = 8000
    # How the service can be accessed from the outside
    # (this typically includes a path prefix and secure scheme in cloud environments)
    service_url_public: str = f"https://{api_host}:{port}/{service_name}"
    # How the service can be accessed from the inside (e.g. for internal service-to-service communication)
    service_url_internal: str = f"http://{service_name}:{port}"
    cors_allowed_origins: list[str] = [service_url_public]

    # OAuth2
    jr_jwt_access_token_signing_key: str = ""

    # Database
    db_name: str = "db"
    db_uri_async: str = "sqlite+aiosqlite:///./db.sqlite"
    echo_sql: bool = False

    # Logging
    log_level: str = "INFO"

    # Debugging
    debug: bool = False

    @property
    def log_level_int(self) -> int:
        try:
            return logging.getLevelNamesMapping()[self.log_level]
        except KeyError:
            logging.error(f"Invalid value for log_level: '{self.log_level}'. Defaulting to 'NOTSET'")
        return logging.NOTSET


_settings = Settings()


def settings() -> Settings:
    return _settings
