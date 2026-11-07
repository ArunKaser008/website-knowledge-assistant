
from app.core.database import SessionLocal
from app.services.rag.answer_service import answer_question


def main():
    db = SessionLocal()

    try:
        question = "What is MentorMuni's refund policy for annual subscriptions?"

        print("\n" + "=" * 80)
        print("QUESTION:", question)
        print("=" * 80)

        result = answer_question(
            db=db,
            question=question,
            top_k=5,
        )

        print("\nANSWER:")
        print(result["answer"])

        print("\nRETRIEVED CHUNKS:")
        print(result["retrieved_chunks"])

        print("\nSOURCES:")

        for source in result["sources"]:
            print(
                f'\n[{source["source_id"]}] '
                f'{source["title"]}'
            )
            print(source["url"])

    except Exception as exc:
        print("\nRAG TEST FAILED:")
        print(type(exc).__name__, str(exc))
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
