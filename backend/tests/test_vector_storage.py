
from uuid import uuid4

from app.core.database import SessionLocal
from app.db.models import PageChunk, WebsitePage
from app.services.embeddings.embedding_service import generate_embedding


def test_vector_storage():
    db = SessionLocal()

    try:
        # Generate a real embedding.
        text = (
            "MentorMuni helps engineering students prepare "
            "for interviews and improve placement readiness."
        )
        embedding = generate_embedding(text)

        print(f"Generated embedding dimensions: {len(embedding)}")

        # Create a temporary parent page.
        page = WebsitePage(
            url=f"https://test.mentormuni.com/{uuid4()}",
            title="Vector Storage Test",
        )

        db.add(page)
        db.flush()

        # Store the chunk and its embedding.
        chunk = PageChunk(
            page_id=page.id,
            chunk_index=0,
            chunk_text=text,
            token_count=20,
            embedding=embedding,
            chunk_metadata={"test": True},
        )

        db.add(chunk)
        db.flush()

        chunk_id = chunk.id

        # Force SQLAlchemy to retrieve the record again.
        db.expire_all()

        stored_chunk = (
            db.query(PageChunk)
            .filter(PageChunk.id == chunk_id)
            .one()
        )

        # Validate the retrieved vector.
        assert stored_chunk.embedding is not None
        assert len(stored_chunk.embedding) == 384

        print(f"Stored chunk ID: {stored_chunk.id}")
        print(f"Retrieved embedding dimensions: {len(stored_chunk.embedding)}")
        print(f"Retrieved text: {stored_chunk.chunk_text}")
        print("Vector storage test: PASSED")

    finally:
        # Remove all temporary test records.
        db.rollback()
        db.close()


if __name__ == "__main__":
    test_vector_storage()
