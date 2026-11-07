
import re
from dataclasses import dataclass
from typing import List

import tiktoken


# Initial chunking configuration
DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 75

# Tokenizer used for estimating chunk size
ENCODING = tiktoken.get_encoding("cl100k_base")


@dataclass
class TextChunk:
    url: str
    title: str
    chunk_index: int
    content: str
    token_count: int


def count_tokens(text: str) -> int:
    """Return the number of tokens in the supplied text."""
    return len(ENCODING.encode(text))


def split_into_paragraphs(text: str) -> List[str]:
    """Split extracted webpage content into meaningful text blocks."""
    paragraphs = []

    for line in text.splitlines():
        cleaned_line = re.sub(r"\s+", " ", line).strip()

        if cleaned_line:
            paragraphs.append(cleaned_line)

    return paragraphs


def chunk_text(
    text: str,
    max_tokens: int = DEFAULT_CHUNK_SIZE,
    overlap_tokens: int = DEFAULT_CHUNK_OVERLAP,
) -> List[str]:
    """
    Split text into token-limited chunks.

    Paragraph boundaries are preserved where possible.
    Oversized paragraphs are split at token boundaries.
    Overlap provides context between consecutive chunks.
    """

    if max_tokens <= 0:
        raise ValueError("max_tokens must be greater than zero")

    if overlap_tokens < 0 or overlap_tokens >= max_tokens:
        raise ValueError(
            "overlap_tokens must be >= 0 and smaller than max_tokens"
        )

    paragraphs = split_into_paragraphs(text)

    if not paragraphs:
        return []

    chunks = []
    current_tokens = []

    for paragraph in paragraphs:
        paragraph_tokens = ENCODING.encode(paragraph)

        # Split paragraphs that exceed the maximum chunk size.
        if len(paragraph_tokens) > max_tokens:

            if current_tokens:
                chunks.append(ENCODING.decode(current_tokens))
                current_tokens = []

            start = 0

            while start < len(paragraph_tokens):
                end = start + max_tokens
                piece = paragraph_tokens[start:end]

                chunks.append(ENCODING.decode(piece))

                if end >= len(paragraph_tokens):
                    break

                start = end - overlap_tokens

            continue

        # Add a paragraph separator when combining paragraphs.
        separator_tokens = ENCODING.encode("\n")
        required_size = (
            len(current_tokens)
            + len(separator_tokens)
            + len(paragraph_tokens)
        )

        if current_tokens and required_size > max_tokens:
            chunks.append(ENCODING.decode(current_tokens))

            # Carry the trailing tokens into the next chunk.
            current_tokens = (
                current_tokens[-overlap_tokens:]
                if overlap_tokens > 0
                else []
            )

        if current_tokens:
            current_tokens.extend(separator_tokens)

        current_tokens.extend(paragraph_tokens)

    if current_tokens:
        chunks.append(ENCODING.decode(current_tokens))

    return [chunk.strip() for chunk in chunks if chunk.strip()]


def chunk_page(
    url: str,
    title: str,
    content: str,
    max_tokens: int = DEFAULT_CHUNK_SIZE,
    overlap_tokens: int = DEFAULT_CHUNK_OVERLAP,
) -> List[TextChunk]:
    """Convert one extracted webpage into structured chunks."""

    raw_chunks = chunk_text(
        text=content,
        max_tokens=max_tokens,
        overlap_tokens=overlap_tokens,
    )

    return [
        TextChunk(
            url=url,
            title=title,
            chunk_index=index,
            content=chunk,
            token_count=count_tokens(chunk),
        )
        for index, chunk in enumerate(raw_chunks)
    ]
