from typing import Dict, Any, Optional
from playwright.sync_api import sync_playwright
import os

class Browser:
    def __init__(self, headless: Optional[bool] = None, nav_timeout_ms: int = 20000):
        self.headless = headless if headless is not None else (os.getenv("HEADLESS", "1") == "1")
        self.nav_timeout_ms = nav_timeout_ms
        self._p = None
        self._browser = None
        self._page = None

    def __enter__(self):
        self._p = sync_playwright().start()
        self._browser = self._p.chromium.launch(
            headless=self.headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        # Set realistic user agent and viewport to avoid bot detection
        self._page = self._browser.new_page(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        self._page.set_default_timeout(self.nav_timeout_ms)
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            if self._browser:
                self._browser.close()
        finally:
            if self._p:
                self._p.stop()

    # --- actions ---
    def goto(self, url: str) -> Dict[str, Any]:
        try:
            self._page.goto(url, wait_until="networkidle")
            self._nudge_lazyload()
        except Exception as e:
            # Return error info without snapshot (page context may be destroyed)
            return {
                "url": url,
                "title": "Navigation Failed",
                "html": "",
                "ax": None,
                "error": f"Failed to navigate to '{url}': {str(e)}"
            }
        return self._snapshot()

    def click(self, selector: Optional[str] = None, text: Optional[str] = None) -> Dict[str, Any]:
        if text:
            self._page.get_by_text(text, exact=False).first.click()
        else:
            self._page.locator(selector).first.click()
        self._page.wait_for_load_state("networkidle")
        self._nudge_lazyload()
        return self._snapshot()

    def type(self, selector: str, value: str, submit: bool = True) -> Dict[str, Any]:
        try:
            self._page.fill(selector, value)
            if submit:
                self._page.keyboard.press("Enter")
            self._page.wait_for_load_state("networkidle")
            self._nudge_lazyload()
        except Exception as e:
            # Try to get snapshot, but fallback if page context is invalid
            try:
                snap = self._snapshot()
                snap["error"] = f"Failed to type into '{selector}': {str(e)}"
                return snap
            except:
                return {
                    "url": self._page.url if self._page else "unknown",
                    "title": "Type Action Failed",
                    "html": "",
                    "ax": None,
                    "error": f"Failed to type into '{selector}': {str(e)}"
                }
        return self._snapshot()

    def snapshot(self) -> Dict[str, Any]:
        return self._snapshot()

    # heuristic site search (if a typical search box exists)
    def find(self, query: str) -> Dict[str, Any]:
        # Try common selectors
        candidates = ["input[type=search]", "input[placeholder*='Search']", "input[name=q]"]
        for sel in candidates:
            loc = self._page.locator(sel)
            if loc.count() > 0:
                # Check if element is visible before trying to interact
                try:
                    if loc.first.is_visible():
                        return self.type(sel, query, submit=True)
                except:
                    continue
        # No search box found - return current state
        snap = self._snapshot()
        snap["error"] = f"No search box found on page for query: '{query}'"
        return snap

    # --- internals ---
    def _nudge_lazyload(self):
        self._page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        self._page.wait_for_timeout(300)

    def _snapshot(self) -> Dict[str, Any]:
        return {
            "url": self._page.url,
            "title": self._page.title(),
            "html": self._page.content(),
            "ax": self._page.accessibility.snapshot()
        }