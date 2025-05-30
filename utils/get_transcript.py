import requests
import re
import os
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


def _extract_video_id(video_id_or_url: str) -> str:
    """
    استخراج شناسه ویدیو از URL یا دریافت مستقیم شناسه
    """
    if "youtube.com" in video_id_or_url or "youtu.be" in video_id_or_url:
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", video_id_or_url)
        if match:
            return match.group(1)
        raise ValueError("لینک یوتیوب نامعتبر است.")
    return video_id_or_url


def _parse_srt_file(file_path: str) -> List[Dict[str, str]]:
    """
    پردازش فایل SRT و استخراج متن با زمان شروع و پایان
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    transcripts = []
    blocks = content.strip().split('\n\n')

    for block in blocks:
        lines = block.split('\n')
        if len(lines) >= 3:
            time_line = lines[1]
            text = ' '.join(lines[2:])

            start_end = time_line.split(' --> ')
            if len(start_end) == 2:
                transcripts.append({
                    'text': text,
                    'start': start_end[0].strip(),
                    'end': start_end[1].strip()
                })

    return transcripts


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
    environment = os.getenv("ENVIRONMENT")
    if environment == "development":
        sample_file = os.path.join(os.path.dirname(
            __file__), "..", "samples", "sample-transcript.srt")

        if not os.path.exists(sample_file):
            raise FileNotFoundError(f"فایل نمونه {sample_file} یافت نشد.")

        return _parse_srt_file(sample_file)

    else:
        try:
            video_id = _extract_video_id(video_url_or_id)
            youtube_transcription_service_url = os.getenv(
                "YOUTUBE_TRANSCRIPT_SERVICE_URL")
            api_url = f"{youtube_transcription_service_url}/transcript?video={video_id}"
            response = requests.get(api_url)
            response.raise_for_status()

            transcript = response.json()
            formatted_transcript = []
            for item in transcript:
                formatted_transcript.append({
                    'text': item['text'],
                    'start': item['start'],
                    'duration': item['duration']
                })
            return formatted_transcript

        except Exception as e:
            print(f"Error while fetching transcript: {e}")
            return None
