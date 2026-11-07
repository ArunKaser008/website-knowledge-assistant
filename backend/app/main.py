import logging

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


app = FastAPI(
    title=settings.APP_NAME,
    description="RAG-based website chatbot API",
    version=settings.APP_VERSION,
)


@app.get("/api/v1/health")
async def health_check():

    return {
        "status": "UP",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/api/v1/health/database")
def database_health_check(db: Session = Depends(get_db)):

    try:
        result = db.execute(text("SELECT 1")).scalar_one()

        return {
            "status": "UP",
            "database": "PostgreSQL",
            "connection": "SUCCESS",
            "test_query_result": result,
        }

    except SQLAlchemyError:
        logger.exception("Database health check failed")

        raise HTTPException(
            status_code=503,
            detail="Database connection failed",
        )