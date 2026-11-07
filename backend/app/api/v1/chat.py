"""API routes for chat."""

"""Chat API endpoint."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from google.genai.errors import APIError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag.answer_service import answer_question


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    try:
        return answer_question(
            db=db,
            question=request.question,
            top_k=request.top_k,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except SQLAlchemyError as exc:
        logger.exception("Knowledge database error")
        raise HTTPException(
            status_code=503,
            detail="Knowledge database is unavailable.",
        ) from exc

    except APIError as exc:
        logger.exception("Gemini API error")
        raise HTTPException(
            status_code=502,
            detail="Answer generation service is temporarily unavailable.",
        ) from exc

    except Exception as exc:
        logger.exception("Unexpected chat API error")
        raise HTTPException(
            status_code=500,
            detail="Unable to process your question right now.",
        ) from exc
