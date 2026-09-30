from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .gemini_service import get_gemini_service
from .schemas import (
    HealthResponse,
    QuizRequest,
    RecommendationRequest,
    SummaryRequest,
    TopicRequest,
)
from .services.explanation_service import explain_topic


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

settings = get_settings()

app = FastAPI(
    title="EduGenie - Google Gemini Powered Learning Assistant",
    version="1.0.0",
    description="AI learning support for Q&A, explanations, summaries, quizzes and learning paths.",
)

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def ai_error(exc: Exception) -> HTTPException:
    message = str(exc)

    if "GEMINI_API_KEY" in message:
        return HTTPException(
            status_code=503,
            detail=message,
        )

    return HTTPException(
        status_code=502,
        detail=message,
    )


@app.get("/", include_in_schema=False)
async def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/api/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        gemini_configured=bool(settings.gemini_api_key),
        model=settings.gemini_model,
    )


@app.get("/qa", include_in_schema=False)
@app.get("/api/qa")
async def answer_question(
    question: str = Query(
        ...,
        min_length=1,
        max_length=5000,
    )
):
    try:
        answer = get_gemini_service().generate(
            question,
            system_instruction=(
                "You are EduGenie, a helpful AI tutor. "
                "Answer accurately and clearly. "
                "Use simple language and examples when useful."
            ),
        )

        return {
            "question": question,
            "answer": answer,
        }

    except Exception as exc:
        raise ai_error(exc)


@app.post("/explain", include_in_schema=False)
@app.post("/api/explain")
async def explanation_api(request: TopicRequest):
    try:
        explanation = explain_topic(request.topic)

        return {
            "topic": request.topic,
            "explanation": explanation,
        }

    except Exception as exc:
        raise ai_error(exc)


@app.post("/summarize", include_in_schema=False)
@app.post("/api/summarize")
async def summarize_api(request: SummaryRequest):
    try:
        prompt = (
            "Summarize the following text in simple language. "
            "Keep the important ideas, remove repetition, "
            "and use a short paragraph followed by bullet points "
            "when useful.\n\n"
            f"TEXT:\n{request.text}"
        )

        summary = get_gemini_service().generate(prompt)

        return {
            "summary": summary,
        }

    except Exception as exc:
        raise ai_error(exc)


@app.post("/quiz", include_in_schema=False)
@app.post("/api/quiz")
async def quiz_api(request: QuizRequest):
    try:
        quiz = get_gemini_service().generate_quiz(
            request.text,
            request.count,
        )

        return {
            "quiz": [
                item.model_dump()
                for item in quiz
            ]
        }

    except Exception as exc:
        raise ai_error(exc)


@app.post("/learn/recommendations", include_in_schema=False)
@app.post("/api/recommendations")
async def recommendations_api(
    request: RecommendationRequest
):
    try:
        prompt = f"""
You are an adaptive AI tutor.

Create a structured learning path for:
{request.topic}

Include:

1. Beginner level with estimated time and key topics.
2. Intermediate level with estimated time and key topics.
3. Advanced level with estimated time and key topics.
4. Practical resources such as documentation,
   books, courses or practice platforms.
5. Adaptive learning tips.

Keep the answer practical and easy for a student to follow.
"""

        recommendations = get_gemini_service().generate(prompt)

        return {
            "topic": request.topic,
            "recommendations": recommendations,
        }

    except Exception as exc:
        raise ai_error(exc)