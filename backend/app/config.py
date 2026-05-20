from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    azure_openai_endpoint: str
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = "gpt-4o"
    azure_openai_api_version: str = "2024-12-01-preview"
    default_azure_region: str = "southeastasia"
    default_iac_format: str = "bicep"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
