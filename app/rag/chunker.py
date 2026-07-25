import re
from typing import List


def split_chunks(content: str, max_chars: int = 400) -> List[str]:
    if not content or not content.strip():
        return []

    parts = re.split(r"(?<=[.!?])\s+", content.strip())
    chunks: List[str] = []
    current: List[str] = []
    current_len = 0

    for part in parts:
        part = part.strip()
        if not part:
            continue
        if current_len + len(part) > max_chars and current:
            chunks.append(" ".join(current))
            current = [part]
            current_len = len(part)
        else:
            current.append(part)
            current_len += len(part) + (1 if current_len else 0)

    if current:
        chunks.append(" ".join(current))

    return chunks if chunks else [content.strip()]
