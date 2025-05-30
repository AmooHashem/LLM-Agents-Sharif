from typing import List, Dict


def _seconds_to_timestamp(sec: float) -> str:
    """
    تبدیل ثانیه به رشته‌ی HH:MM:SS.ss
    """
    hours = int(sec // 3600)
    minutes = int((sec % 3600) // 60)
    seconds = sec % 60
    # فرمت گذاری با دقت اعشار دو رقم برای ثانیه
    return f"{hours:02d}:{minutes:02d}:{seconds:05.2f}"


def transcripts_to_prompt_format(
    transcripts: List[Dict[str, float]]
) -> List[str]:
    """
    ورودی: لیستی از دیکشنری‌ها به شکل
        {
          "text": <متن>,
          "start": <زمان شروع بر حسب ثانیه>,
          "duration": <مدت بر حسب ثانیه>
        }
    خروجی: لیستی از رشته‌ها با فرمت:
        [HH:MM:SS.ss - HH:MM:SS.ss] متن
    """
    prompt_lines = []
    for entry in transcripts:
        text = entry.get("text", "").strip()
        start = float(entry.get("start", 0.0))
        duration = float(entry.get("duration", 0.0))

        end = start + duration
        start_ts = _seconds_to_timestamp(start)
        end_ts = _seconds_to_timestamp(end)

        line = f"[{start_ts} - {end_ts}] {text}"
        prompt_lines.append(line)

    return prompt_lines
