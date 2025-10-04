from typing import Dict, Any
from .navigator import Browser
from .filterer import ContextFilterer

class Controller:
    def __init__(self, browser: Browser, filterer: ContextFilterer, goal: str):
        self.browser = browser
        self.filterer = filterer
        self.goal = goal

    def run(self, action: Dict[str, Any]) -> Dict[str, Any]:
        t = action["type"]
        args = action.get("args", {})
        if t == "NAVIGATE":
            # Block direct navigation - agent must use CLICK to navigate
            raw = {
                "url": self.browser._page.url if self.browser._page else "unknown",
                "title": "Navigation Blocked",
                "html": "",
                "ax": None,
                "error": "NAVIGATE action is not allowed. Use CLICK to navigate via links on the page."
            }
        elif t == "CLICK":
            raw = self.browser.click(args.get("selector"), args.get("text"))
        elif t == "TYPE":
            raw = self.browser.type(args["selector"], args["text"], args.get("submit", True))
        elif t == "FIND":
            raw = self.browser.find(args["query"])
        elif t == "EXTRACT":
            raw = self.browser.snapshot()
            raw["success"] = "Page snapshot taken"
        elif t == "STOP":
            raw = self.browser.snapshot()
            if "answer" in args:
                raw["success"] = f"Task completed. Answer: {args['answer']}"
            else:
                raw["success"] = "Task completed"
        else:
            raise ValueError(f"Unknown action {t}")
        obs_md = self.filterer.to_markdown(raw, goal=self.goal)
        return {"raw": raw, "observation_md": obs_md}