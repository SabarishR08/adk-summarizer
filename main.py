import os
import json
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from agent import root_agent


APP_NAME = "summarizer"
DEFAULT_USER_ID = "user1"

app = FastAPI(title="ADK Text Summarizer", version="1.0.0")
session_service = InMemorySessionService()


class InputRequest(BaseModel):
    input: str = Field(..., min_length=1, description="Text to summarize")
    user_id: Optional[str] = Field(default=None, description="Optional caller id")


class StructuredSummaryResponse(BaseModel):
    title: str
    bullets: list[str]


async def run_agent_prompt(prompt: str, user_id: str) -> str:
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    session = await session_service.create_session(app_name=APP_NAME, user_id=user_id)
    new_message = Content(role="user", parts=[Part(text=prompt)])

    response_text = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session.id,
        new_message=new_message,
    ):
        if not event.is_final_response() or not event.content:
            continue
        if event.content.parts and event.content.parts[0].text:
            response_text = event.content.parts[0].text

    if not response_text:
        raise HTTPException(status_code=500, detail="No summary returned by agent")

    return response_text


def parse_structured_json(text: str) -> StructuredSummaryResponse:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=500,
            detail="Agent returned non-JSON structured output",
        ) from exc

    title = payload.get("title", "") if isinstance(payload, dict) else ""
    bullets = payload.get("bullets", []) if isinstance(payload, dict) else []

    if not isinstance(title, str) or not title.strip():
        raise HTTPException(status_code=500, detail="Structured output missing title")
    if not isinstance(bullets, list) or not bullets:
        raise HTTPException(status_code=500, detail="Structured output missing bullets")

    normalized_bullets = [str(item).strip() for item in bullets if str(item).strip()]
    if not normalized_bullets:
        raise HTTPException(status_code=500, detail="Structured output bullets are empty")
    if len(normalized_bullets) < 3 or len(normalized_bullets) > 5:
        raise HTTPException(
            status_code=500,
            detail="Structured output must contain 3-5 bullets",
        )

    return StructuredSummaryResponse(title=title.strip(), bullets=normalized_bullets)


@app.get("/")
def health() -> dict:
    return {
        "status": "ok",
        "agent": "text_summarizer",
        "model": os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
    }


@app.post("/summarize")
async def summarize(req: InputRequest) -> dict:
    if not req.input.strip():
        raise HTTPException(status_code=400, detail="input must not be empty")

    user_id = req.user_id or DEFAULT_USER_ID
    summary = await run_agent_prompt(req.input, user_id)

    return {"summary": summary}


@app.post("/summarize/structured", response_model=StructuredSummaryResponse)
async def summarize_structured(req: InputRequest) -> StructuredSummaryResponse:
    if not req.input.strip():
        raise HTTPException(status_code=400, detail="input must not be empty")

    user_id = req.user_id or DEFAULT_USER_ID
    structured_prompt = (
        "Summarize the following text and return ONLY valid JSON with this schema: "
        "{\"title\": string, \"bullets\": string[]}. "
        "Use 3-5 bullets. Do not include markdown fences or any extra keys. "
        f"Text: {req.input}"
    )
    raw = await run_agent_prompt(structured_prompt, user_id)
    return parse_structured_json(raw)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
