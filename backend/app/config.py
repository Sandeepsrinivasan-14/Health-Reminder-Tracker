"""Application settings, loaded from environment variables (and an optional .env file)."""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Health Reminder Tracker API"
    environment: str = Field(default="development", description="development | production | test")

    # Database. SQLite for local dev; set a PostgreSQL URL in production.
    database_url: str = "sqlite:///./health_tracker.db"

    # Timezone used to decide which doses are "today" (IANA name).
    timezone: str = "Asia/Kolkata"

    # Comma-separated list of allowed CORS origins ("*" only makes sense in development).
    cors_origins: str = "http://localhost:8501"

    # Shared secret the frontend sends in the X-API-Key header. Empty = auth disabled (dev only).
    api_key: str = ""

    # Optional LLM (Groq, OpenAI-compatible endpoint). Without a key a rule-based assistant is used.
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    groq_base_url: str = "https://api.groq.com/openai/v1"

    # Optional Twilio SMS / WhatsApp.
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""

    # Optional SMTP email.
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from: str = ""

    @field_validator("database_url")
    @classmethod
    def _normalise_postgres_scheme(cls, value: str) -> str:
        # Render / Heroku / Neon sometimes hand out postgres:// URLs, which SQLAlchemy rejects.
        if value.startswith("postgres://"):
            value = value.replace("postgres://", "postgresql+psycopg://", 1)
        elif value.startswith("postgresql://"):
            value = value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def llm_enabled(self) -> bool:
        return bool(self.groq_api_key)

    @property
    def sms_enabled(self) -> bool:
        return bool(self.twilio_account_sid and self.twilio_auth_token and self.twilio_from_number)

    @property
    def email_enabled(self) -> bool:
        return bool(self.smtp_username and self.smtp_password)


@lru_cache
def get_settings() -> Settings:
    return Settings()
