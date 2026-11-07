
"""Website ingestion pipeline: crawl, extract, chunk, embed, and store."""

import hashlib
from datetime import datetime, timezone
from unittest import result

from sqlalchemy.orm import Session

from app.db.models import PageChunk, WebsitePage
from app.services.crawler.sitemap import discover_sitemap_urls
from app.services.crawler.browser_crawler import render_page
from app.services.crawler.extractor import extract_page
from app.services.chunker import chunk_page
from app.services.embeddings.embedding_service import generate_embeddings


def ingest_website(
    db: Session,
    website_url: str,
    max_pages: int = 50,
) -> dict:
    """
    Ingest website content into PostgreSQL.

    Existing unchanged pages are skipped.
    Changed pages have their old chunks replaced.
    Each page is committed independently.
    """

    urls = discover_sitemap_urls(
        website_url,
        max_pages=max_pages,
    )

    result = {
        "discovered_urls": len(urls),
        "processed_pages": 0,
        "skipped_pages": 0,
        "failed_pages": 0,
        "total_chunks": 0,
        "errors": [],
    }

    for url in urls:
        try:
            # 1. Render the page using Playwright.
            rendered = render_page(url)

            if rendered.error or not rendered.html:
                raise RuntimeError(
                    rendered.error or "Page rendering returned empty HTML"
                )

            # 2. Extract meaningful page content.
            extracted = extract_page(
                rendered.url,
                rendered.html,
                rendered.title,
            )

            if extracted.error or not extracted.content.strip():
                raise RuntimeError(
                  extracted.error or "No meaningful content extracted"
                )

            # Skip pages with insufficient content.
            if extracted.word_count < 50:
                result["skipped_pages"] += 1
                continue

            # 3. Generate a content hash.
            content_hash = hashlib.sha256(
                f"{extracted.title}\n{extracted.content}".encode("utf-8")
            ).hexdigest()

            # 4. Check whether the page already exists.
            page = (
                db.query(WebsitePage)
                .filter(WebsitePage.url == extracted.url)
                .first()
            )

            if page and page.content_hash == content_hash:
                page.last_crawled_at = datetime.now(timezone.utc)
                page.is_active = True

                db.commit()
                result["skipped_pages"] += 1
                continue

            # 5. Create or update the website page.
            if page is None:
                page = WebsitePage(
                    url=extracted.url,
                    title=extracted.title,
                )
                db.add(page)
                db.flush()
            else:
                page.title = extracted.title

                # Remove old chunks before replacing them.
                db.query(PageChunk).filter(
                    PageChunk.page_id == page.id
                ).delete(synchronize_session=False)

            # 6. Split the extracted content into chunks.
            chunks = chunk_page(
                extracted.url,
                extracted.title,
                extracted.content,
            )

            if not chunks:
                raise RuntimeError("Chunking produced no chunks")

            # 7. Generate embeddings for all chunks.
            embeddings = generate_embeddings(
                [chunk.content for chunk in chunks]
            )

            if len(chunks) != len(embeddings):
                raise RuntimeError(
                    "Chunk count and embedding count do not match"
                )

            # 8. Store chunks and their embeddings.
            for chunk, embedding in zip(chunks, embeddings):
                db.add(
                    PageChunk(
                        page_id=page.id,
                        chunk_index=chunk.chunk_index,
                        chunk_text=chunk.content,
                        token_count=chunk.token_count,
                        embedding=embedding,
                        chunk_metadata={
                            "source_url": extracted.url,
                            "page_title": extracted.title,
                        },
                    )
                )

            # 9. Update page metadata.
            page.content_hash = content_hash
            page.last_crawled_at = datetime.now(timezone.utc)
            page.is_active = True

            db.commit()

            result["processed_pages"] += 1
            result["total_chunks"] += len(chunks)

        except Exception as exc:
            db.rollback()

            result["failed_pages"] += 1
            result["errors"].append({
                "url": url,
                "error": str(exc),
            })

    return result
