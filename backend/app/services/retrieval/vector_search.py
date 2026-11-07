
"""Semantic search using PostgreSQL and pgvector."""

from sqlalchemy.orm import Session

from app.db.models import PageChunk, WebsitePage
from app.services.embeddings.embedding_service import generate_embedding


def search_similar_chunks(
    db: Session,
    query: str,
    top_k: int = 5,
) -> list[dict]:
    """
    Find the most relevant website chunks using cosine similarity.

    Args:
        db: Active SQLAlchemy database session.
        query: User's natural-language question.
        top_k: Maximum number of results.

    Returns:
        Relevant chunks with source information and similarity scores.
    """

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if top_k < 1:
        raise ValueError("top_k must be greater than zero.")

    # 1. Generate embedding for the user's question.
    query_embedding = generate_embedding(query)

    # 2. Calculate cosine distance and retrieve relevant chunks.
    distance = PageChunk.embedding.cosine_distance(query_embedding)

    results = (
        db.query(
            PageChunk.id.label("chunk_id"),
            PageChunk.chunk_text,
            PageChunk.chunk_index,
            PageChunk.token_count,
            WebsitePage.url,
            WebsitePage.title,
            distance.label("distance"),
        )
        .join(
            WebsitePage,
            PageChunk.page_id == WebsitePage.id,
        )
        .filter(
            PageChunk.embedding.isnot(None),
            WebsitePage.is_active.is_(True),
        )
        .order_by(distance)
        .limit(top_k)
        .all()
    )

    # 3. Format results.
    search_results = []

    for row in results:
        similarity = 1.0 - float(row.distance)

        search_results.append({
            "chunk_id": row.chunk_id,
            "chunk_index": row.chunk_index,
            "content": row.chunk_text,
            "token_count": row.token_count,
            "source_url": row.url,
            "page_title": row.title,
            "similarity": round(similarity, 4),
        })

    return search_results
