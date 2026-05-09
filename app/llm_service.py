import json
import os
from typing import Any, Optional


def build_tutoring_prompt(
    activity_text: str,
    learning_objectives: list[str],
    student_message: str,
    chat_history: Optional[list[dict[str, str]]] = None,
) -> str:
    chat_history = chat_history or []

    return f"""
You are an academic tutoring assistant for an in-class learning activity.

Your job is to guide the student step by step.

STRICT RULES:
1. Always respond in English.
2. Ask exactly ONE guiding question.
3. Do NOT give the final answer directly.
4. Do NOT reveal or list the hidden learning objectives.
5. Do NOT mention that hidden learning objectives exist.
6. Use terminology from the activity text.
7. Keep the response short, supportive, and academic.
8. Do not include scoring.
9. Do not ask multiple questions in one response.
10. The student should think and explain, not just receive the answer.

ACTIVITY TEXT:
{activity_text}

HIDDEN LEARNING OBJECTIVES FOR SYSTEM USE ONLY:
{json.dumps(learning_objectives, ensure_ascii=False)}

RECENT CHAT HISTORY:
{json.dumps(chat_history[-6:], ensure_ascii=False)}

LATEST STUDENT MESSAGE:
{student_message}

Return ONLY valid JSON in this exact format:
{{
  "reply": "one short guiding question in English",
  "reason": "brief reason for teacher/debugging"
}}
""".strip()


def _remove_markdown_json_fence(text: str) -> str:
    cleaned = text.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned.replace("```json", "", 1).strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```", "", 1).strip()

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()

    return cleaned


def _safe_parse_json(text: str) -> dict[str, Any]:
    cleaned = _remove_markdown_json_fence(text)

    try:
        parsed = json.loads(cleaned)

        if isinstance(parsed, dict):
            return parsed

        return {
            "reply": str(parsed),
            "reason": "Model returned JSON but not an object."
        }

    except Exception:
        return {
            "reply": cleaned,
            "reason": "Model did not return valid JSON."
        }


def _force_single_question(reply: str) -> str:
    reply = (reply or "").strip()

    if not reply:
        return "What part of the activity supports your thinking?"

    # If the model gives more than one question, keep only the first one.
    if reply.count("?") > 1:
        reply = reply.split("?")[0].strip() + "?"

    # If the model gives a statement, convert it into a question-like prompt.
    if "?" not in reply:
        reply = reply.rstrip(".") + "?"

    return reply


def call_gemini(prompt: str) -> dict[str, Any]:
    from google import genai

    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")

    if not api_key:
        return {
            "reply": "What part of the activity helped you reach that idea?",
            "reason": "GEMINI_API_KEY is missing."
        }

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model=model,
        contents=prompt
    )

    return _safe_parse_json(response.text)


def call_openai(prompt: str) -> dict[str, Any]:
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        return {
            "reply": "What part of the activity helped you reach that idea?",
            "reason": "OPENAI_API_KEY is missing."
        }

    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model=model,
        input=prompt
    )

    return _safe_parse_json(response.output_text)


def generate_llm_tutoring_reply(
    activity_text: str,
    learning_objectives: list[str],
    student_message: str,
    chat_history: Optional[list[dict[str, str]]] = None,
) -> dict[str, str]:
    prompt = build_tutoring_prompt(
        activity_text=activity_text,
        learning_objectives=learning_objectives,
        student_message=student_message,
        chat_history=chat_history
    )

    provider = os.getenv("LLM_PROVIDER", "gemini").lower().strip()

    if provider == "openai":
        result = call_openai(prompt)
    else:
        result = call_gemini(prompt)

    reply = _force_single_question(result.get("reply", ""))

    return {
        "reply": reply,
        "reason": result.get("reason", "")
    }