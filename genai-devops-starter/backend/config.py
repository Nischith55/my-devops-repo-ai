from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_env: str = 'dev'
    mock_mode: bool = True

    backend_host: str = '0.0.0.0'
    backend_port: int = 8000

    vllm_base_url: str = 'http://localhost:8001/v1'
    vllm_model: str = 'TinyLlama/TinyLlama-1.1B-Chat-v1.0'
    vllm_api_key: str = 'EMPTY'


settings = Settings()
