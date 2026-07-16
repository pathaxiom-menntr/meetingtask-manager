from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str

    SECRET_KEY: str

    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15

    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_VERSION: str
    AZURE_OPENAI_DEPLOYMENT: str

    # Comma-separated list of allowed frontend origins.
    # Leave empty for dev (localhost fallback is used).
    # Example for production: "https://app.yourdomain.com"
    ALLOWED_ORIGINS: str = ""

    # Max transcript characters sent to AI (prevents runaway costs/timeouts)
    MAX_TRANSCRIPT_CHARS: int = 200_000

    # ── AI Pipeline tuning (all optional — sensible defaults provided) ──────
    # Max characters per transcript chunk for long-meeting support (≈ 8K tokens)
    AI_CHUNK_SIZE_CHARS: int = 32_000

    # Enable the second LLM validation pass (catches missed tasks & hallucinations)
    AI_VALIDATION_PASS: bool = True

    # Max retry attempts on Azure OpenAI API errors (exponential back-off)
    AI_MAX_RETRIES: int = 3

    # Tasks with confidence below this floor are dropped (0.50 = keep almost everything)
    AI_MIN_CONFIDENCE: float = 0.50

    class Config:
        env_file = ".env"


settings = Settings()
