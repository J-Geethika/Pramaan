from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Pramaan API"
    environment: str = "development"
    database_url: str = "postgresql+psycopg2://localhost:5432/pramaan"
    secret_key: str = "change-me-in-env"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    qr_signing_secret: str = "change-me-qr-secret"
    apaar_official_integration_enabled: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
