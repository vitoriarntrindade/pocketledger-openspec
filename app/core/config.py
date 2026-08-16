from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    service_name: str = "pocketledger"
    environment: str = "development"
    log_level: str = "INFO"

    database_url: str = (
        "postgresql+psycopg://pocketledger:pocketledger@db:5432/pocketledger"
    )

    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 60

    password_min_length: int = 8

    default_page_size: int = 20
    max_page_size: int = 100

    cors_allowed_origins: str = ""

    rate_limit_max_attempts: int = 5
    rate_limit_window_seconds: int = 60

    otel_exporter_otlp_endpoint: str = "jaeger:4317"
    otel_enabled: bool = True


def assert_production_ready(settings: Settings) -> None:
    """Fail-closed guard: refuse to start outside development with placeholder secrets."""
    if settings.environment in ("development", "test"):
        return

    known_placeholders = {
        "change-me-in-production",
        "dev-only-secret-change-me",
    }
    if settings.jwt_secret in known_placeholders:
        raise RuntimeError(
            "JWT_SECRET must be overridden outside development. "
            "Generated a strong random secret and set it via environment or .env."
        )

    if "pocketledger:pocketledger" in settings.database_url:
        raise RuntimeError(
            "DATABASE_URL must not use default development credentials outside development. "
            "Set DB_USER, DB_PASSWORD, and DB_NAME via environment or .env."
        )


settings = Settings()
