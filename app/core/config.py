from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Design Ref: §10.3 — 필수 환경변수 목록
    database_url: str
    google_places_api_key: str
    app_env: str = "local"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
