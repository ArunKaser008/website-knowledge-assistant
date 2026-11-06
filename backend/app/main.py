
from fastapi import FastAPI

app = FastAPI(
    title="Website Knowledge Assistant",
    description="RAG-based website chatbot API",
    version="1.0.0",
)


@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "UP",
        "application": "Website Knowledge Assistant",
        "version": "1.0.0",
    }
