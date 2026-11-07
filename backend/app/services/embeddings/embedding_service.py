
"""Local text embedding generation using Sentence Transformers."""

from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384
BATCH_SIZE = 16


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Load the embedding model once and reuse it."""
    model = SentenceTransformer(MODEL_NAME, device="cpu")

    if model.get_embedding_dimension() != EMBEDDING_DIMENSION:
        raise ValueError(
            f"Expected {EMBEDDING_DIMENSION} dimensions, "
            f"got {model.get_embedding_dimension()}"
        )

    return model


def _split_into_model_windows(
    text: str,
    model: SentenceTransformer,
) -> tuple[list[str], list[int]]:
    """
    Split text into windows that fit the model's token limit.

    This prevents long chunks from being silently truncated.
    """
    tokenizer = model.tokenizer
    token_ids = tokenizer.backend_tokenizer.encode(
        text,
        add_special_tokens=False,
     ).ids

    special_tokens = tokenizer.num_special_tokens_to_add(pair=False)
    window_size = model.max_seq_length - special_tokens

    windows = []
    token_counts = []

    for start in range(0, len(token_ids), window_size):
        window_ids = token_ids[start : start + window_size]

        window_text = tokenizer.backend_tokenizer.decode(
            window_ids,
             skip_special_tokens=True,
            )

        if window_text.strip():
            windows.append(window_text)
            token_counts.append(len(window_ids))

    return windows, token_counts


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generate normalized 384-dimensional embeddings.

    Long texts are embedded in smaller windows. Their embeddings
    are combined using token-count-weighted averaging.
    """
    if not texts:
        return []

    if any(not text or not text.strip() for text in texts):
        raise ValueError("Input texts must not be empty.")

    model = get_embedding_model()

    all_windows = []
    text_window_ranges = []

    for text in texts:
        windows, token_counts = _split_into_model_windows(text, model)

        if not windows:
            raise ValueError("Unable to generate embedding for empty text.")

        start = len(all_windows)
        all_windows.extend(windows)
        end = len(all_windows)

        text_window_ranges.append((start, end, token_counts))

    window_embeddings = model.encode(
        all_windows,
        batch_size=BATCH_SIZE,
        convert_to_numpy=True,
        normalize_embeddings=False,
        show_progress_bar=False,
    )

    results = []

    for start, end, token_counts in text_window_ranges:
        embeddings = window_embeddings[start:end]

        weights = np.array(token_counts, dtype=np.float32)
        weights /= weights.sum()

        combined_embedding = np.average(
            embeddings,
            axis=0,
            weights=weights,
        )

        # L2 normalization for cosine similarity retrieval.
        norm = np.linalg.norm(combined_embedding)

        if norm == 0:
            raise ValueError("Generated embedding has zero magnitude.")

        normalized_embedding = combined_embedding / norm

        results.append(normalized_embedding.tolist())

    return results


def generate_embedding(text: str) -> list[float]:
    """Generate one normalized embedding."""
    return generate_embeddings([text])[0]
"""Text embedding generation."""
