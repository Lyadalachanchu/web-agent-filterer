import time
from typing import Any

def trunc(s: str, n: int = 300) -> str:
    return (s[: n - 3] + "...") if s and len(s) > n else (s or "")

def timestamp() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")