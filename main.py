from extract_instructional_points import extract_instructional_points
from utils.get_transcript_full_text import extract_transcript_text
from fastapi import FastAPI, HTTPException, Query
from utils.get_transcript import get_transcript
import json
import os
from dotenv import load_dotenv

load_dotenv()


app = FastAPI(
    title="Educational Video Compressor",
    description="Take a YouTube link (or ID) and return it as a course.",
    version="1.0.0"
)


@app.get("/create-course")
async def create_course(video: str = Query(..., description="YouTube video URL or ID")):

    transcript = get_transcript(video)

    transcript_full_text = extract_transcript_text(transcript)

    instructional_points = extract_instructional_points(transcript_full_text)

    # Simulate processing
    return instructional_points


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
