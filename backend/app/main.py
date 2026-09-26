"""Earth Whisper read-only data API.

Serves the verified Step 10 investigation subset and the Step 11 case file.
It does not compute, score, classify or predict anything, and it contains no
LLM integration.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import candidates, casefile, health
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Earth Whisper API",
    description=(
        "Read-only access to the verified Earth Whisper candidate evidence. "
        "Values are served as produced by the scientific pipeline: no probabilities, "
        "no confidence scores and no confirmed event labels."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(candidates.router, prefix="/api")
app.include_router(casefile.router, prefix="/api")


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, _exc: Exception) -> JSONResponse:
    """Return a clean JSON error without exposing stack traces."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error while reading the verified data outputs."},
    )


def main() -> None:
    import uvicorn

    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=False)


if __name__ == "__main__":
    main()
