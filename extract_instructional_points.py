import os
from openai import OpenAI
import tiktoken
import json
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client with configurable base URL
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)

# Default to widely available model
MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
MAX_INPUT_TOKENS_PER_CHUNK = 30000


def extract_instructional_points(full_text: str) -> list[str]:
    """
    [Function docstring remains unchanged]
    """
    # 1. Token‐encode and chunk text
    encoding = tiktoken.get_encoding("cl100k_base")
    token_ids = encoding.encode(full_text)
    chunks_text = [
        encoding.decode(token_ids[i: i + MAX_INPUT_TOKENS_PER_CHUNK])
        for i in range(0, len(token_ids), MAX_INPUT_TOKENS_PER_CHUNK)
    ]

    # 2. Summarize each chunk using the client
    chunk_summaries = []
    for chunk in chunks_text:
        prompt = (
            "Using only the information presented in this educational video chunk, "
            "identify and summarize its key instructional points without including any content that isn’t explicitly covered in the video.\n\n"
            "-----\n"
            f"{chunk}\n"
            "-----\n"
        )
        response = client.chat.completions.create(  # Updated client call
            model=MODEL,
            messages=[
                {"role": "system",
                    "content": "You specialize in distilling instructional content."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            max_tokens=1024,
        )

        summary_text = response.choices[0].message.content.strip()
        chunk_summaries.append(summary_text)

    # 3. Merge summaries and extract points
    combined = "\n\n--- End of Chunk Summary ---\n\n".join(chunk_summaries)
    merge_prompt = (
        "Merge these summaries and extract instructional points as a JSON array:\n\n"
        f"{combined}\n\n"
        "Output format: ['point1', 'point2', ...]"
    )

    merge_response = client.chat.completions.create(  # Updated client call
        model=MODEL,
        messages=[
            {"role": "system", "content": "Output JSON arrays of key instructional points."},
            {"role": "user", "content": merge_prompt},
        ],
        temperature=0.0,
        response_format={"type": "json_object"},  # Enforce JSON output
        max_tokens=2048,
    )

    raw_output = merge_response.choices[0].message.content.strip()
    try:
        data = json.loads(raw_output)
        # Handle different JSON structures
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "points" in data:
            return data["points"]
        elif isinstance(data, dict):
            return list(data.values())
        else:
            raise ValueError("Unexpected JSON format")
    except (json.JSONDecodeError, ValueError):
        # Fallback: split lines if JSON parsing fails
        return [line.strip(" -•") for line in raw_output.splitlines() if line.strip()]
