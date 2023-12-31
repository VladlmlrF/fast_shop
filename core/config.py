from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASS: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

DATABASE_URL = (
    f"postgresql+asyncpg://{settings.DB_USER}:"
    f"{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

PASSWORD_VALIDATOR = (
    "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
)


class AuthSettings(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15


auth_settings = AuthSettings()
