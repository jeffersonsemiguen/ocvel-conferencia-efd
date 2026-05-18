from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str = "dev-secret-key"
    environment: str = "development"
    upload_dir: str = "./uploads"

    model_config = {"env_file": ".env"}


settings = Settings()
