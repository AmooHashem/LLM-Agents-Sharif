from typing import List, Dict


def extract_transcript_text(transcript: List[Dict[str, float]]) -> str:
    """
    دریافت تمام متن‌ها از یک ترنسکرایپت و ادغام آن‌ها در یک رشته واحد.

    ورودی:
        transcript: لیستی از دیکشنری‌ها با شکل:
            [
                {
                    "text": "متن زیرنویس",
                    "start": 5.03,
                    "duration": 2.53
                },
                ...
            ]

    خروجی:
        یک رشته حاوی تمام مقادیر “text” به ترتیب، جدا شده با فاصله.
    """
    # جمع‌آوری تکست‌ها در یک لیست
    texts = [item["text"] for item in transcript if "text" in item]

    # ادغام همه‌ی متون با یک فاصلهٔ واحد
    return " ".join(texts)
