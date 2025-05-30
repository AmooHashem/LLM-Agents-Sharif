import os
import re
import json
import tiktoken
from openai import OpenAI
from dotenv import load_dotenv
from typing import List

from utils.chunk_transcripts import chunk_transcripts
from utils.segments import sort_and_merge_segments
from utils.transcripts_to_prompt_format import transcripts_to_prompt_format

load_dotenv()

# Initialize OpenAI client with configurable base URL
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)

# Default to widely available model
MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
MAX_INPUT_TOKENS_PER_CHUNK = 30000


def build_prompt(transcript_lines: List[str], educational_points: List[str]) -> str:
    """
    Constructs the prompt by inserting the educational points and formatted transcript into the template.
    """
    # 1. Format educational points
    points_section = "1. The whole video has these instructional points:\n\n"
    for idx, point in enumerate(educational_points, start=1):
        points_section += f"   * Point {idx}: {point}\n"

    # 2. Format transcript for the prompt
    transcript_section = "\n2. The full transcript of this video section with exact timestamps for the start of each sentence:\n\n"
    for line in transcript_lines:
        # Expect format: "[HH:MM:SS.ss - HH:MM:SS.ss] some text"
        match = re.match(
            r"\[(?P<start>[\d:.]+)\s*-\s*[\d:.]+\]\s*(?P<text>.+)", line)
        if match:
            start_time = match.group("start")
            text = match.group("text").strip()
            transcript_section += f"   [{start_time}] “{text}.”\n"

    # 3. Add extraction instructions
    extraction_instructions = """
    * The final output should be a list of segments in this format:
        ```
        00:02:15 – 00:02:35 | Purpose of this segment 
        00:05:10 – 00:05:30 | Purpose of this segment
        00:08:45 – 00:09:05 | Purpose of this segment
        …
        ```
    """

    # Combine all parts into the final prompt
    prompt = (
        "You are acting as a professor and need to tell a student—who has very little time to prepare for an exam—"
        "exactly which important parts of this section of the video he/she should watch. Follow these steps:\n\n"
        + points_section
        + transcript_section
        + extraction_instructions
    )
    return prompt


def extract_segments(transcript_lines: List[str], educational_points: List[str]) -> List[str]:
    """
    Takes a list of transcript lines in the format "[HH:MM:SS.ss - HH:MM:SS.ss] text"
    and a list of educational points, constructs the prompt, sends it to the OpenAI API,
    and extracts the resulting time segments with descriptions.

    Returns a list of strings, each in the format "HH:MM:SS – HH:MM:SS | Description".
    """
    # Build the prompt
    prompt = build_prompt(transcript_lines, educational_points)

    # Call OpenAI's chat completion endpoint
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        max_tokens=2048,
    )

    # Extract the assistant's reply text
    reply_text = response.choices[0].message.content.strip()

    # Use regex to find all time segments with a description, e.g.:
    # "HH:MM:SS – HH:MM:SS | Some description"
    segment_pattern = re.compile(
        r"(?P<start>\d{2}:\d{2}:\d{2}(?:\.\d{2})?)\s*–\s*"
        r"(?P<end>\d{2}:\d{2}:\d{2}(?:\.\d{2})?)"
        r"\s*\|\s*(?P<desc>.+)"
    )

    segments_with_desc = []
    for match in segment_pattern.finditer(reply_text):
        start = match.group("start")
        end = match.group("end")
        desc = match.group("desc").strip()
        segments_with_desc.append(f"{start} – {end} | {desc}")

    return segments_with_desc


def extract_transcripts_segments(transcripts, instructional_points):
    chunked_transcripts = chunk_transcripts(transcripts)
    segments = []
    for chunk in chunked_transcripts:
        formatted_transcripts = transcripts_to_prompt_format(chunk)
        chunk_segments = extract_segments(formatted_transcripts,
                                          instructional_points)
        segments += sort_and_merge_segments(chunk_segments)
    return segments
