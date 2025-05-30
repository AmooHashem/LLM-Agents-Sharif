import re
from typing import List, Tuple


def parse_time(time_str: str) -> float:
    """
    Parses a time string "HH:MM:SS" or "HH:MM:SS.ss" into total seconds (float).
    """
    parts = time_str.split(":")
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2])
    return hours * 3600 + minutes * 60 + seconds


def format_time(sec: float) -> str:
    """
    Formats a float number of seconds into "HH:MM:SS" if whole seconds,
    or "HH:MM:SS.ss" with two decimal places if fractional.
    """
    hours = int(sec // 3600)
    minutes = int((sec % 3600) // 60)
    seconds_float = sec % 60
    if abs(seconds_float - round(seconds_float)) < 1e-6:
        # Treat as whole seconds
        seconds_int = int(round(seconds_float))
        return f"{hours:02d}:{minutes:02d}:{seconds_int:02d}"
    else:
        return f"{hours:02d}:{minutes:02d}:{seconds_float:05.2f}"


def sort_and_merge_segments(segments: List[str]) -> List[str]:
    """
    Given a list of segments in the format "HH:MM:SS – HH:MM:SS" (optionally with decimals),
    sorts them by start time, and merges any consecutive segments whose gap is <= 1 second.

    Returns a new list of merged segments in the same string format.
    """
    # 1. Parse all segments into a list of tuples (start_seconds, end_seconds)
    parsed: List[Tuple[float, float]] = []
    pattern = re.compile(r"^(?P<start>[\d:.]+)\s*–\s*(?P<end>[\d:.]+)$")

    for seg in segments:
        m = pattern.match(seg.strip())
        if not m:
            raise ValueError(f"Invalid segment format: {seg}")
        start_sec = parse_time(m.group("start"))
        end_sec = parse_time(m.group("end"))
        parsed.append((start_sec, end_sec))

    # 2. Sort by start time
    parsed.sort(key=lambda x: x[0])

    # 3. Merge segments with gap <= 1 second
    merged: List[Tuple[float, float]] = []
    for start, end in parsed:
        if not merged:
            merged.append((start, end))
        else:
            prev_start, prev_end = merged[-1]
            # If the gap between prev_end and current start is <= 1 second, merge
            if start - prev_end <= 1.0:
                # Extend the previous end to max(prev_end, end)
                merged[-1] = (prev_start, max(prev_end, end))
            else:
                merged.append((start, end))

    # 4. Format back into strings
    result: List[str] = []
    for start_sec, end_sec in merged:
        start_str = format_time(start_sec)
        end_str = format_time(end_sec)
        result.append(f"{start_str} – {end_str}")

    return result


# Example usage:
if __name__ == "__main__":
    segments = [
        "00:00:14.79 – 00:00:32.10",
        "00:00:35.37 – 00:00:42.51",
        "00:00:53.01 – 00:01:09.68",
        "00:01:53.96 – 00:02:12.59",
        "00:03:02.93 – 00:03:10.29",
        "00:05:58.82 – 00:06:15.20",
        "00:06:56.42 – 00:07:05.33",
        "00:10:17.08 – 00:10:22.87",
        "00:11:00.94 – 00:11:20.41",
        "00:15:27.54 – 00:15:43.40",
        "00:30:15 – 00:33:17",
        "00:33:32 – 00:34:09",
        "00:45:39 – 00:47:13",
        "00:45:39 – 00:47:13",
        "00:47:18 – 00:48:14",
        "00:59:48 – 01:00:31",
        "01:01:26 – 01:02:00",
        "01:04:00 – 01:05:03",
        "01:00:31 – 01:01:26",
        "01:02:00 – 01:02:24",
        "01:13:57 – 01:14:11",
        "01:14:24 – 01:14:37",
        "01:19:05 – 01:19:13",
        "01:15:08 – 01:16:13",
        "01:17:15 – 01:17:22",
        "01:17:49 – 01:18:12",
        "01:18:54 – 01:19:08",
        "01:19:11 – 01:19:25"
    ]
    merged = sort_and_merge_segments(segments)
    for m in merged:
        print(m)
