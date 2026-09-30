from pydantic import BaseModel, Field


class TopicRequest(BaseModel):

    topic: str = Field(
        min_length=1,
        max_length=500
    )


class SummaryRequest(BaseModel):

    text: str = Field(
        min_length=1,
        max_length=20000
    )


class QuizRequest(BaseModel):

    text: str = Field(
        min_length=1,
        max_length=12000
    )

    count: int = Field(
        default=3,
        ge=1,
        le=5
    )


class RecommendationRequest(BaseModel):

    topic: str = Field(
        min_length=1,
        max_length=500
    )


class QuizQuestion(BaseModel):

    question: str

    options: list[str] = Field(
        min_length=4,
        max_length=4
    )

    answer: str


class HealthResponse(BaseModel):

    status: str

    gemini_configured: bool

    model: str