import os

from google.adk.agents import Agent
from dotenv import load_dotenv


load_dotenv()

# Support common codelab env aliases while keeping SDK-native names.
if not os.getenv("GOOGLE_CLOUD_PROJECT") and os.getenv("PROJECT_ID"):
    os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("PROJECT_ID", "")
if not os.getenv("GOOGLE_CLOUD_LOCATION") and os.getenv("LOCATION"):
    os.environ["GOOGLE_CLOUD_LOCATION"] = os.getenv("LOCATION", "")
if not os.getenv("GOOGLE_GENAI_USE_VERTEXAI"):
    has_vertex_config = os.getenv("GOOGLE_CLOUD_PROJECT") and os.getenv("GOOGLE_CLOUD_LOCATION")
    if has_vertex_config:
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"


def prepare_text(text: str) -> str:
    """Light cleanup to keep model input stable before summarization."""
    return " ".join(text.split())


def resolve_model_name() -> str:
    """Resolve model from env with backward-compatible key support."""
    return (
        os.getenv("MODEL")
        or os.getenv("GEMINI_MODEL")
        or "gemini-2.5-flash"
    )


MODEL_NAME = resolve_model_name()

root_agent = Agent(
    name="text_summarizer",
    model=MODEL_NAME,
    description="Summarizes user-provided text.",
    instruction=(
        "You are an expert summarization assistant. "
        "Return only a concise 2-3 sentence summary in plain text. "
        "Preserve factual meaning, remove repetition, and avoid adding new claims."
    ),
)
