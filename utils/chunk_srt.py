import re
from datetime import timedelta


def parse_srt_timestamp(ts_str):
    """
    Parse a timestamp of the form "HH:MM:SS,mmm" into a timedelta.
    """
    hours, minutes, seconds_ms = ts_str.split(":")
    seconds, ms = seconds_ms.split(",")
    return timedelta(
        hours=int(hours),
        minutes=int(minutes),
        seconds=int(seconds),
        milliseconds=int(ms)
    )


def format_timedelta(td):
    total_seconds = int(td.total_seconds())
    ms = int(td.microseconds / 1000)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02},{ms:03}"


def chunk_srt(srt_path):
    """
    Read an SRT file from `srt_path` and split it into overlapping 20-minute chunks
    with 5-minute overlap between consecutive chunks.

    Returns:
        List of chunks, where each chunk is a list of transcript‐entry dicts:
            {
                "index":      <int>,
                "start":      <timedelta>,
                "end":        <timedelta>,
                "text":       <str>       # possibly multiple lines separated by "\n"
            }
    """
    # 1) Read entire SRT file and split by blank lines into entries
    with open(srt_path, "r", encoding="utf-8") as f:
        raw = f.read().strip()

    # Split on double-newlines (some SRTs use "\r\n"; normalize first)
    raw = raw.replace("\r\n", "\n")
    entries = raw.split("\n\n")

    # 2) Parse each entry into a dict: index, start (timedelta), end (timedelta), text
    parsed_entries = []
    time_pattern = re.compile(
        r"(\d+):(\d+):(\d+,\d+)\s*-->\s*(\d+):(\d+):(\d+,\d+)")
    for entry in entries:
        lines = entry.split("\n")
        if len(lines) < 2:
            continue  # skip any malformed block
        idx_line = lines[0].strip()
        try:
            idx = int(idx_line)
        except ValueError:
            # Sometimes the index is missing or malformed; skip if so
            continue

        times_line = lines[1].strip()
        m = time_pattern.match(times_line)
        if not m:
            continue  # skip if time format is not correct

        # Build timestamp strings
        start_ts = f"{m.group(1)}:{m.group(2)}:{m.group(3)}"
        end_ts = f"{m.group(4)}:{m.group(5)}:{m.group(6)}"
        start_td = parse_srt_timestamp(start_ts)
        end_td = parse_srt_timestamp(end_ts)

        # The remaining lines (2:) are the transcript text
        text = "\n".join(lines[2:])

        parsed_entries.append({
            "index": idx,
            "start": start_td,
            "end": end_td,
            "text": text,
        })

    if not parsed_entries:
        return []

    # 3) Determine the time span: start at the first transcript's start, end at the last transcript's end
    first_start = parsed_entries[0]["start"]
    last_end = parsed_entries[-1]["end"]

    # 4) Build chunks of length 20 minutes, stepping every 15 minutes (i.e. 5-min overlap)
    chunk_length = timedelta(minutes=20)
    step = timedelta(minutes=15)

    chunks = []
    current_chunk_start = first_start
    while current_chunk_start < last_end:
        current_chunk_end = current_chunk_start + chunk_length

        # Select all entries whose start time falls within [chunk_start, chunk_end)
        chunk_entries = [
            e for e in parsed_entries
            if e["start"] >= current_chunk_start and e["start"] < current_chunk_end
        ]

        chunks.append(chunk_entries)
        current_chunk_start += step

    return chunks


def chunk_srt_to_files(srt_path, output_prefix="chunk"):
    chunks = chunk_srt(srt_path)
    for i, chunk in enumerate(chunks, start=1):
        filename = f"{output_prefix}_{i}.srt"
        with open(filename, "w", encoding="utf-8") as f:
            # دوباره ساب‌تایتل‌ها رو با فرمت استاندارد srt می‌نویسیم
            for j, entry in enumerate(chunk, start=1):
                f.write(str(j) + "\n")
                start_str = format_timedelta(entry["start"])
                end_str = format_timedelta(entry["end"])
                f.write(f"{start_str} --> {end_str}\n")
                f.write(entry["text"] + "\n\n")

    print(f"{len(chunks)} chunks saved with prefix '{output_prefix}_'.")


chunk_srt_to_files("./sample.srt")
