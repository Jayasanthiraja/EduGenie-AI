from ..gemini_service import get_gemini_service


def explain_topic(topic: str) -> str:

    prompt = (
        f"Explain the concept '{topic}' "
        "in simple, clear language for a school "
        "or college student. "
        "Use a short definition, key points, "
        "and one simple example. "
        "Avoid unnecessary jargon."
    )

    return get_gemini_service().generate(prompt)