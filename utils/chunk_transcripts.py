def chunk_transcripts(transcripts):
    """
    Split a list of transcript entries into overlapping 20-minute chunks
    with 5-minute overlap between consecutive chunks.

    Each transcript entry should be a dict of the form:
        {
            "text": <str>,
            "start": <float>,    # start time in seconds
            "duration": <float>  # duration in seconds
        }

    Returns:
        List of chunks, where each chunk is a list of transcript‐entry dicts.
    """
    if not transcripts:
        return []

    # 1) Compute each entry's end time, and find the overall time span
    for e in transcripts:
        e["_end"] = e["start"] + e["duration"]

    first_start = min(e["start"] for e in transcripts)
    last_end = max(e["_end"] for e in transcripts)

    # 2) Set chunk parameters (in seconds)
    chunk_length = 20 * 60   # 20 minutes = 1200 seconds
    step = 15 * 60   # advance by 15 minutes = 900 seconds

    chunks = []
    current_start = first_start

    # 3) Slide a 20-minute window, stepping every 15 minutes
    while current_start < last_end:
        current_end = current_start + chunk_length

        # 4) Collect all entries whose start time falls within [current_start, current_end)
        chunk_entries = [
            # drop the internal "_end" key
            {k: v for k, v in e.items() if k != "_end"}
            for e in transcripts
            if e["start"] >= current_start and e["start"] < current_end
        ]

        chunks.append(chunk_entries)
        current_start += step

    return chunks
