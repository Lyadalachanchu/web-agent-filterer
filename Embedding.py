"""Embedding helpers.

Functions accept an optional OpenAI client. If no client is passed, this module
will attempt to create one by loading a .env (via python-dotenv) and
instantiating OpenAI() (the same approach used in `make_query.py`).
This keeps callers flexible: they can supply their own client or rely on
the environment-backed default.
"""

from __future__ import annotations

import time
from typing import Any, List, Optional

from tqdm import tqdm
import dotenv

# Attempt to load environment from parent .env if present (same pattern as make_query.py)
try:
    dotenv.load_dotenv()
except Exception:
    # If python-dotenv isn't installed, we'll rely on environment variables already set
    pass

# Try to create a module-level default client (will use OPENAI_API_KEY from env if present)
_default_client: Optional[Any] = None
try:
    from openai import OpenAI

    try:
        _default_client = OpenAI()
    except Exception:
        # if OPENAI_API_KEY not set or OpenAI init fails, leave as None
        _default_client = None
except Exception:
    _default_client = None


def get_embedding(client: Optional[Any], text: str, model: str = "text-embedding-3-small", retries: int = 3, backoff: float = 1.0) -> Optional[List[float]]:
    """Return embedding for a single string using the provided OpenAI client.

    Parameters
    - client: an initialized OpenAI client (eg. OpenAI(api_key=...))
    - text: input text
    - model: embedding model name
    - retries/backoff: simple retry behavior on transient errors

    Returns the embedding (list of floats) or None for None input.
    """
    # resolve client: priority -> explicit client arg, module default client
    cli = client or _default_client
    if cli is None:
        raise RuntimeError("OpenAI client not provided and default client could not be initialized. Provide a client or set OPENAI_API_KEY in the environment.")

    if text is None:
        return None
    text = str(text).replace("\n", " ")

    for attempt in range(1, retries + 1):
        try:
            resp = cli.embeddings.create(input=[text], model=model)
            return resp.data[0].embedding
        except Exception:
            if attempt < retries:
                time.sleep(backoff * attempt)
                continue
            raise


def batch_get_embeddings(client: Optional[Any], texts: List[Optional[str]], model: str = "text-embedding-3-small", batch_size: int = 64) -> List[Optional[List[float]]]:
    """Compute embeddings for a list of texts using the provided client.

    The caller is responsible for creating the OpenAI client with their own key.
    The function preserves ordering and None entries.
    """
    # resolve client
    cli = client or _default_client
    if cli is None:
        raise RuntimeError("OpenAI client not provided and default client could not be initialized. Provide a client or set OPENAI_API_KEY in the environment.")

    results: List[Optional[List[float]]] = []

    for i in tqdm(range(0, len(texts), batch_size), desc="batches"):
        batch = [str(t).replace("\n", " ") if t is not None else None for t in texts[i : i + batch_size]]

        indices = [j for j, t in enumerate(batch) if t is not None]
        inputs = [batch[j] for j in indices]

        if not inputs:
            results.extend([None] * len(batch))
            continue

        resp = cli.embeddings.create(input=inputs, model=model)
        embeddings = [r.embedding for r in resp.data]

        it = iter(embeddings)
        for t in batch:
            if t is None:
                results.append(None)
            else:
                results.append(next(it))

    return results


__all__ = ["get_embedding", "batch_get_embeddings"]
