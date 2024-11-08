import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file
env = os.getenv('ENVIRONMENT')
dotenv_path = f'.env.{env}'

class Settings(BaseSettings):
    # FastAPI
    FASTAPI_PORT: int
    
    # PostgreSQL Configuration
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int
    DB_HOST: str
    DATABASE_URL: str

    # JWT secret key and other sensitive configurations
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Redis Configuration
    REDIS_PORT: int
    REDIS_URL: str

    # pgAdmin Configuration (if using pgAdmin)
    PGADMIN_DEFAULT_EMAIL: str
    PGADMIN_DEFAULT_PASSWORD: str
    PGADMIN_PORT: int

    # SMTP Email Settings
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str

    # Verification links
    EMAIL_VERIFICATION_LINK: str
    PASSWORD_RESET_LINK: str

    # App Passwords
    ADMIN_PASSWORD: str
    USER_PASSWORD: str

    class Config:
        env_file = dotenv_path

# Create an instance of the settings
settings = Settings()

class TestSettings(Settings):
    
    class Config:
        env_file = ".env.test"

# Create an instance of the test_settings
test_settings = TestSettings()
