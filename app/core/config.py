import os
from pydantic import BaseModel


class Settings(BaseModel):
    APP_ENV: str = os.getenv("APP_ENV", "dev")
    API_BASE_PATH: str = os.getenv("API_BASE_PATH", "/api")
    API_KEY: str = os.getenv("API_KEY", "")

    MONGO_URI: str = os.getenv("MONGO_URI", "")
    MONGO_DB: str = os.getenv("MONGO_DB", "homecollection")

    QR_HMAC_SECRET: str = os.getenv("QR_HMAC_SECRET", "")
    QR_SIG_TTL_SECONDS: int = int(os.getenv("QR_SIG_TTL_SECONDS", "900"))

    DB_CREATE_INDEXES: bool = os.getenv(
        "DB_CREATE_INDEXES", "true").lower() == "true"

    ALLOWED_ORIGINS: list[str] = [
        o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()
    ]


settings = Settings()
