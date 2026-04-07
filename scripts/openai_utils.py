import time

from openai import APIConnectionError, APITimeoutError, InternalServerError, RateLimitError


class QuotaExceededError(RuntimeError):
    pass


def create_chat_completion(client, model, messages, max_retries=5, base_delay=5):
    for attempt in range(1, max_retries + 1):
        try:
            return client.chat.completions.create(
                model=model,
                messages=messages,
            )
        except RateLimitError as exc:
            error = getattr(exc, "body", {}) or {}
            code = error.get("error", {}).get("code")
            if code == "insufficient_quota":
                raise QuotaExceededError("OpenAI quota exceeded.") from exc
            if attempt == max_retries:
                raise
            time.sleep(base_delay * attempt)
        except (APIConnectionError, APITimeoutError, InternalServerError):
            if attempt == max_retries:
                raise
            time.sleep(base_delay * attempt)
