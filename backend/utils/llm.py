"""
Ollama LLM client — reusable call_llm() function.
All agents use this single entrypoint.
"""
print("🔥 USING UPDATED LLM FILE")
import json
import time
import logging
import httpx
import asyncio
import re
from typing import Optional

logger = logging.getLogger(__name__)

# ── Config ─────────────────────────────────────────────────────────────────
OLLAMA_URL   = "http://localhost:11434/api/generate"
MODEL        = "llama3:8b"
MAX_RETRIES  = 3
RETRY_DELAY  = 2.0          # seconds (doubles each attempt)
TIMEOUT      = 900.0        # 🔥 increased from 120 → 300


async def call_llm(
    prompt: str,
    system_prompt: str,
    temperature: float = 0.7,
    request_id: str = "?",
) -> str:
    """
    Send a prompt to local Ollama and return the response text.
    """

    payload = {
        "model": MODEL,
        "prompt": _build_prompt(system_prompt, prompt),
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": 2048,
        },
    }

    last_error: Optional[Exception] = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            t0 = time.time()

            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                resp = await client.post(OLLAMA_URL, json=payload)

            elapsed = round((time.time() - t0) * 1000, 1)

            if resp.status_code == 200:
                data = resp.json()
                text = data.get("response", "").strip()

                logger.info(
                    "[%s] Ollama OK — model=%s attempt=%d latency=%dms tokens=%s",
                    request_id, MODEL, attempt, elapsed,
                    data.get("eval_count", "?"),
                )

                return text

            elif resp.status_code == 404:
                raise RuntimeError(
                    f"Ollama model '{MODEL}' not found. "
                    f"Run: ollama pull {MODEL}"
                )

            else:
                body = resp.text[:300]
                logger.warning(
                    "[%s] Ollama HTTP %d (attempt %d/%d): %s",
                    request_id, resp.status_code, attempt, MAX_RETRIES, body,
                )
                last_error = RuntimeError(f"HTTP {resp.status_code}: {body}")

        except httpx.ConnectError as e:
            logger.warning(
                "[%s] Ollama not reachable (attempt %d/%d) — "
                "is 'ollama serve' running? Error: %s",
                request_id, attempt, MAX_RETRIES, e,
            )
            last_error = e

        except httpx.TimeoutException as e:
            logger.warning(
                "[%s] Ollama timeout after %.0fs (attempt %d/%d)",
                request_id, TIMEOUT, attempt, MAX_RETRIES,
            )
            last_error = e

        except RuntimeError:
            raise

        except Exception as e:
            logger.error("[%s] Unexpected LLM error: %s", request_id, e)
            last_error = e

        if attempt < MAX_RETRIES:
            wait = RETRY_DELAY * attempt
            logger.info("[%s] Retrying in %.1fs…", request_id, wait)
            await asyncio.sleep(wait)

    raise RuntimeError(
        f"Ollama call failed after {MAX_RETRIES} attempts. Last error: {last_error}"
    )


def _build_prompt(system_prompt: str, user_prompt: str) -> str:
    return (
        f"<|begin_of_text|>"
        f"<|start_header_id|>system<|end_header_id|>\n\n"
        f"{system_prompt.strip()}"
        f"<|eot_id|>"
        f"<|start_header_id|>user<|end_header_id|>\n\n"
        f"{user_prompt.strip()}"
        f"<|eot_id|>"
        f"<|start_header_id|>assistant<|end_header_id|>\n\n"
    )


def extract_json(raw: str, request_id: str = "?") -> dict:
    """
    🔥 Robust JSON extraction (minimal fix, no redesign)
    """

    text = raw.strip()

    # ── Remove markdown blocks ─────────────────────────────
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            cleaned = part.strip()
            if cleaned.startswith("json"):
                cleaned = cleaned[4:].strip()
            if cleaned.startswith("{"):
                text = cleaned
                break

    # ── Try direct parse first ─────────────────────────────
    try:
        return json.loads(text)
    except:
        pass

    # ── Extract JSON using regex ───────────────────────────
    match = re.search(r"\{.*\}", text, re.DOTALL)

    if match:
        candidate = match.group(0)

        # Try normal parse
        try:
            return json.loads(candidate)
        except:
            pass

        # 🔥 Fix incomplete JSON (VERY IMPORTANT)
        try:
            fixed = candidate + "}"
            return json.loads(fixed)
        except:
            pass

        # 🔥 Remove trailing commas
        try:
            fixed = re.sub(r",\s*([}\]])", r"\1", candidate)
            return json.loads(fixed)
        except:
            pass

    raise ValueError(
        f"[{request_id}] No JSON object found in LLM response.\n"
        f"Raw (first 400 chars): {raw[:400]}"
    )