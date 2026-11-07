
"""Pydantic schemas for chatbot requests and responses."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming chatbot question."""

    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's question about MentorMuni",
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum number of relevant chunks to retrieve",
    )


class ChatSource(BaseModel):
    """Source reference used to generate an answer."""

    source_id: int
    title: str
    url: str


class ChatResponse(BaseModel):
    """Chatbot response returned to the frontend."""

    question: str
    answer: str
    sources: list[ChatSource]
    retrieved_chunks: int
