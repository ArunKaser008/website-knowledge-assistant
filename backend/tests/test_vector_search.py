from app.core.database import SessionLocal
from app.services.retrieval.vector_search import search_similar_chunks


queries = [
    "How does MentorMuni help students prepare for placements?",
    "What services does MentorMuni offer to colleges?",
    "How can students check their interview readiness?",
]

db = SessionLocal()

try:
    for query in queries:
        print("\n" + "=" * 80)
        print(f"QUERY: {query}")
        print("=" * 80)

        results = search_similar_chunks(
            db=db,
            query=query,
            top_k=3,
        )

        if not results:
            print("No matching chunks found.")
            continue

        for index, result in enumerate(results, start=1):
            print(f"\nResult #{index}")
            print(f"Page: {result['page_title']}")
            print(f"URL: {result['source_url']}")
            print(f"Similarity: {result['similarity']}")
            print(f"Content: {result['content'][:500]}")

finally:
    db.close()