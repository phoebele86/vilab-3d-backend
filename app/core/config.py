from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    llm_base_url: str = "http://localhost:11434/v1"
    llm_model: str = "vilab-qwen"
    llm_api_key: str = "ollama"
    embedding_model: str = "bge-m3"
    embedding_dim: int = 1024
    cors_origins: list[str] = ["http://localhost:5173"]
    assets_dir: str | None = None
    jwt_secret: str


settings = Settings()
