import os
import orjson
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
from openai import OpenAI


# Simple wrapper for OpenAI Chat Completions


class LLM:
    def __init__(self, model: str | None = None):
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4")
        self.client = OpenAI()


    @retry(wait=wait_exponential(multiplier=1, min=1, max=8), stop=stop_after_attempt(3))
    def complete(self, system: str, user: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
        )
        return resp.choices[0].message.content


    @staticmethod
    def parse_json_block(text: str) -> Dict[str, Any]:
        """Extract first JSON object from text (between ```json ... ``` or bare)."""
        s = text.strip()
        if "```" in s:
            # naive block extraction
            start = s.find("```")
            end = s.find("```", start + 3)
            if end > start:
                block = s[start + 3 : end]
                if block.lstrip().startswith("json"):
                    block = block.split("\n", 1)[1]
                s = block
        return orjson.loads(s)