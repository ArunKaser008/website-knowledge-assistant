
"""Pydantic schemas for chatbot requests and responses."""

from typing import Literal

from pydantic import BaseModel, Field


class ChatHistoryMessage(BaseModel):
    """A previous message in the conversation."""

    role: Literal["user", "assistant"]
    content: str = Field(
        ...,
        min_length=1,
        max_length=4000,
    )


class ChatRequest(BaseModel):
    """Incoming chatbot question with optional conversation history."""

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

    conversation_history: list[ChatHistoryMessage] = Field(
        default_factory=list,
        max_length=10,
        description="Previous conversation messages for contextual responses",
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
