from pydantic_settings import SettingsConfigDict, BaseSettings

class Settings(BaseSettings):
    
    DATABASE_URL: str
    SECRET_KEY: str
    SECRET_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    CLOUDFLARE_TURNSTILE_SECRET_KEY: str = "1x0000000000000000000000000000000AA"
    CLOUDFLARE_TURNSTILE_SITE_KEY: str = "1x0000000000000000000000000000000AA"
    DISABLE_CAPTCHA_VERIFICATION: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore", # ignore extra env vars
        case_sensitive=True  #makes it casesensitive
    )
settings = Settings()