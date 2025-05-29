import re
import os
from youtube_transcript_api import YouTubeTranscriptApi
from pydantic_settings import BaseSettings
from typing import List, Dict


class Settings(BaseSettings):
    openai_api_key: str
    openai_api_base: str
    ENVIRONMENT: str

    class Config:
        env_file = ".env"


settings = Settings()


def extract_video_id(video_id_or_url: str) -> str:
    """
    استخراج شناسه ویدیو از URL یا دریافت مستقیم شناسه
    """
    if "youtube.com" in video_id_or_url or "youtu.be" in video_id_or_url:
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", video_id_or_url)
        if match:
            return match.group(1)
        raise ValueError("لینک یوتیوب نامعتبر است.")
    return video_id_or_url


def parse_srt_file(file_path: str) -> List[Dict[str, str]]:
    """
    پردازش فایل SRT و استخراج متن با زمان شروع و پایان
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    subtitles = []
    blocks = content.strip().split('\n\n')

    for block in blocks:
        lines = block.split('\n')
        if len(lines) >= 3:
            time_line = lines[1]
            text = ' '.join(lines[2:])

            start_end = time_line.split(' --> ')
            if len(start_end) == 2:
                subtitles.append({
                    'text': text,
                    'start': start_end[0].strip(),
                    'end': start_end[1].strip()
                })

    return subtitles


def get_transcript(video_url_or_id: str) -> List[Dict[str, str]]:
    """
    دریافت ترنسکرایپت با فرمت:
    [
        {
            "text": "متن زیرنویس",
            "start": "00:00:00,000",
            "end": "00:00:02,340"
        },
        ...
    ]
    """
    if settings.ENVIRONMENT == "development":
        sample_file = os.path.join(os.path.dirname(__file__), "sample.srt")

        if not os.path.exists(sample_file):
            raise FileNotFoundError(f"فایل نمونه {sample_file} یافت نشد.")

        return parse_srt_file(sample_file)
    else:
        try:
            video_id = extract_video_id(video_url_or_id)
            transcript = YouTubeTranscriptApi.get_transcript(video_id)

            # تبدیل فرمت زمان از ثانیه به فرمت SRT
            formatted_transcript = []
            for item in transcript:
                start_seconds = item['start']
                end_seconds = start_seconds + item['duration']

                formatted_transcript.append({
                    'text': item['text'],
                    'start': seconds_to_srt_time(start_seconds),
                    'end': seconds_to_srt_time(end_seconds)
                })

            return formatted_transcript
        except Exception as e:
            print(f"Error: {e}")
            return None


def seconds_to_srt_time(seconds: float) -> str:
    """
    تبدیل زمان از ثانیه به فرمت SRT (HH:MM:SS,mmm)
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds_remainder = seconds % 60
    millis = int((seconds_remainder - int(seconds_remainder)) * 1000)

    return f"{hours:02d}:{minutes:02d}:{int(seconds_remainder):02d},{millis:03d}"
