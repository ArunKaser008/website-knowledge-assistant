
from app.core.database import SessionLocal
from app.services.ingestion_service import ingest_website


def main():
    db = SessionLocal()

    try:
        result = ingest_website(
            db=db,
            website_url="https://www.mentormuni.com",
            max_pages=19,
        )

        print("\n========== INGESTION SUMMARY ==========")

        for key, value in result.items():
            print(f"{key}: {value}")

        print("=======================================\n")

    finally:
        db.close()


if __name__ == "__main__":
    main()
