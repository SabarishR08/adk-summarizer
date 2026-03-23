import os

from google.adk.agents import Agent
from google.adk.tools import FunctionTool


def prepare_text(text: str) -> str:
    """Light cleanup to keep model input stable before summarization."""
    return " ".join(text.split())


prepare_text_tool = FunctionTool(func=prepare_text)

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

root_agent = Agent(
    name="text_summarizer",
    model=MODEL_NAME,
    description="Summarizes user-provided text.",
    instruction=(
        "You are a concise summarization assistant. "
        "Summarize the user text in 2-3 clear sentences. "
        "Preserve factual meaning and avoid adding new claims. "
        "Use the prepare_text tool before producing the final summary."
    ),
    tools=[prepare_text_tool],
)
