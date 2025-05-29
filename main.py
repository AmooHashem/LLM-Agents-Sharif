# main.py

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import json
from get_transcript import get_transcript
import os

app = FastAPI(
    title="Educational Video Compressor",
    description="Take a YouTube link (or ID) and return it as a course.",
    version="1.0.0"
)


class TranscriptResponse(BaseModel):
    transcript: str


@app.get("/transcript", response_model=TranscriptResponse)
def get_transcript_endpoint(video: str = Query(..., description="لینک یا ID ویدئو")):
    try:
        # دریافت مستقیم ترنسکرایپت بدون استفاده از agent
        result = get_transcript(video)
        if result is None:
            error_msg = "متأسفانه ترنسکرایپت پیدا نشد یا خطایی رخ داد."
            return TranscriptResponse(transcript=error_msg)

        # تبدیل به JSON
        json_result = json.dumps(result, ensure_ascii=False, indent=2)
        return TranscriptResponse(transcript=json_result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
