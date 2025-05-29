# main.py

from fastapi import FastAPI, HTTPException, Query
from pydantic_settings import BaseSettings
from pydantic import BaseModel
import json
import os


class Settings(BaseSettings):
    openai_api_key: str
    openai_api_base: str
    ENVIRONMENT: str
    YOUTUBE_SUBTITLE_SERVICE_URL: str

    class Config:
        env_file = ".env"


settings = Settings()


app = FastAPI(
    title="Educational Video Compressor",
    description="Take a YouTube link (or ID) and return it as a course.",
    version="1.0.0"
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
