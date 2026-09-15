from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Design Ref: §10.3 — 필수 환경변수 목록
    database_url: str
    google_places_api_key: str
    app_env: str = "local"
    cors_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
