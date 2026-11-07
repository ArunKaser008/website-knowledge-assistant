
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlsplit

from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError
)


USER_AGENT = "WebsiteKnowledgeAssistant/1.0"

NAVIGATION_TIMEOUT = 30000

MAX_PAGE_SIZE = 5 * 1024 * 1024

ALLOWED_HOST = "mentormuni.com"


@dataclass
class RenderedPage:
    """
    Represents a JavaScript-rendered website page.
    """

    url: str
    title: Optional[str] = None
    html: Optional[str] = None
    text: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self):
        return {
            "url": self.url,
            "title": self.title,
            "html": self.html,
            "text": self.text,
            "error": self.error
        }


def validate_url(url: str) -> bool:
    """
    Validate that the URL belongs to MentorMuni.
    """

    try:
        parsed = urlsplit(url)

        if parsed.scheme not in ("http", "https"):
            return False

        if not parsed.hostname:
            return False

        if parsed.username or parsed.password:
            return False

        hostname = parsed.hostname.lower().removeprefix("www.")

        return hostname == ALLOWED_HOST

    except ValueError:
        return False


def render_page(url: str) -> RenderedPage:
    """
    Launch Chromium and retrieve JavaScript-rendered content.
    Browser cleanup happens before Playwright shuts down.
    """

    if not validate_url(url):
        return RenderedPage(
            url=url,
            error="URL is not allowed"
        )

    try:

        with sync_playwright() as playwright:

            browser = playwright.chromium.launch(
                headless=True
            )

            try:

                context = browser.new_context(
                    user_agent=USER_AGENT,
                    java_script_enabled=True
                )

                page = context.new_page()

                page.set_default_navigation_timeout(
                    NAVIGATION_TIMEOUT
                )

                response = page.goto(
                    url,
                    wait_until="domcontentloaded"
                )

                if response is None:
                    return RenderedPage(
                        url=url,
                        error="No HTTP response received"
                    )

                if response.status >= 400:
                    return RenderedPage(
                        url=url,
                        error=f"HTTP error: {response.status}"
                    )

                if not validate_url(page.url):
                    return RenderedPage(
                        url=url,
                        error="Redirected outside the allowed website"
                    )

                try:
                    page.wait_for_load_state(
                        "networkidle",
                        timeout=10000
                    )

                except PlaywrightTimeoutError:
                    pass

                page.wait_for_timeout(1500)

                title = page.title()

                html = page.content()

                if len(html.encode("utf-8")) > MAX_PAGE_SIZE:
                    return RenderedPage(
                        url=url,
                        error="Rendered page exceeds maximum size"
                    )

                text = page.locator("body").inner_text(
                    timeout=10000
                )

                return RenderedPage(
                    url=url,
                    title=title,
                    html=html,
                    text=text
                )

            finally:
                # Close browser BEFORE Playwright context exits.
                browser.close()

    except PlaywrightTimeoutError:

        return RenderedPage(
            url=url,
            error="Page navigation or rendering timed out"
        )

    except Exception as exc:

        return RenderedPage(
            url=url,
            error=f"Browser rendering failed: {str(exc)}"
        )
