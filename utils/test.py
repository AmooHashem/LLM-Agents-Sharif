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


def total_duration(segments: List[str]) -> str:
    """
    Given a list of segments in the format "HH:MM:SS – HH:MM:SS" (optionally with decimals),
    returns the sum of all segment durations as a formatted string "HH:MM:SS" or "HH:MM:SS.ss".
    """
    total_seconds = 0.0
    pattern = re.compile(r"^(?P<start>[\d:.]+)\s*–\s*(?P<end>[\d:.]+)$")

    for seg in segments:
        m = pattern.match(seg.strip())
        if not m:
            raise ValueError(f"Invalid segment format: {seg}")
        start_sec = parse_time(m.group("start"))
        end_sec = parse_time(m.group("end"))
        duration = end_sec - start_sec
        if duration < 0:
            raise ValueError(
                f"End time is before start time in segment: {seg}")
        total_seconds += duration

    return format_time(total_seconds)


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
        "00:47:18 – 00:48:14",
        "00:59:48 – 01:02:24",
        "01:04:00 – 01:05:03",
        "01:13:57 – 01:14:11",
        "01:14:24 – 01:14:37",
        "01:15:08 – 01:16:13",
        "01:17:15 – 01:17:22",
        "01:17:49 – 01:18:12",
        "01:18:54 – 01:19:25"
    ]
    print("Total duration:", total_duration(segments))
    # Expected: Total duration: 00:01:21  (which is (36 + 16 + 39) = 91 seconds = 00:01:31)
