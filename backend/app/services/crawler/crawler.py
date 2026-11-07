
import time

from dataclasses import dataclass, asdict
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import (
    Request,
    build_opener,
    HTTPRedirectHandler
)


USER_AGENT = "WebsiteKnowledgeAssistant/1.0"

REQUEST_TIMEOUT = 20
MAX_PAGE_SIZE = 5 * 1024 * 1024  # 5 MB


class SameHostRedirectHandler(HTTPRedirectHandler):
    """
    Allow redirects only to the original website host.
    """

    def __init__(self, allowed_host: str):
        super().__init__()
        self.allowed_host = allowed_host.lower().removeprefix("www.")

    def redirect_request(self, req, fp, code, msg, headers, newurl):

        parsed = urlsplit(newurl)

        if parsed.scheme not in ("http", "https"):
            raise HTTPError(
                newurl, code, "Invalid redirect scheme", headers, fp
            )

        target_host = (parsed.hostname or "").lower().removeprefix("www.")

        if target_host != self.allowed_host:
            raise HTTPError(
                newurl, code, "Cross-domain redirect blocked", headers, fp
            )

        return super().redirect_request(
            req, fp, code, msg, headers, newurl
        )


@dataclass
class CrawledPage:
    """
    Structured result for a crawled website page.
    """

    url: str
    status_code: Optional[int] = None
    content_type: Optional[str] = None
    html: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self):
        return asdict(self)


def fetch_page(url: str) -> CrawledPage:
    """
    Fetch HTML content from a single website URL.

    Returns structured page information.
    """

    parsed = urlsplit(url)

    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return CrawledPage(
            url=url,
            error="Invalid URL"
        )

    allowed_host = parsed.hostname.lower().removeprefix("www.")

    opener = build_opener(
        SameHostRedirectHandler(allowed_host)
    )

    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml"
        }
    )

    try:

        with opener.open(
            request,
            timeout=REQUEST_TIMEOUT
        ) as response:

            final_url = response.geturl()
            final_parsed = urlsplit(final_url)

            final_host = (
                (final_parsed.hostname or "")
                .lower()
                .removeprefix("www.")
            )

            if (
                final_parsed.scheme not in ("http", "https")
                or final_host != allowed_host
            ):
                return CrawledPage(
                    url=url,
                    error="Invalid final redirect URL"
                )

            status_code = response.status

            content_type = response.headers.get(
                "Content-Type", ""
            )

            if "text/html" not in content_type.lower() and \
               "application/xhtml+xml" not in content_type.lower():

                return CrawledPage(
                    url=url,
                    status_code=status_code,
                    content_type=content_type,
                    error="Non-HTML content skipped"
                )

            content_length = response.headers.get("Content-Length")

            if content_length and int(content_length) > MAX_PAGE_SIZE:
                return CrawledPage(
                    url=url,
                    status_code=status_code,
                    content_type=content_type,
                    error="Page exceeds maximum allowed size"
                )

            html_bytes = response.read(MAX_PAGE_SIZE + 1)

            if len(html_bytes) > MAX_PAGE_SIZE:
                return CrawledPage(
                    url=url,
                    status_code=status_code,
                    content_type=content_type,
                    error="Page exceeds maximum allowed size"
                )

            charset = response.headers.get_content_charset() or "utf-8"

            html = html_bytes.decode(
                charset,
                errors="replace"
            )

            return CrawledPage(
                url=url,
                status_code=status_code,
                content_type=content_type,
                html=html
            )

    except HTTPError as exc:

        return CrawledPage(
            url=url,
            status_code=exc.code,
            error=f"HTTP error: {exc.code}"
        )

    except (URLError, TimeoutError, OSError, ValueError) as exc:

        return CrawledPage(
            url=url,
            error=f"Request failed: {str(exc)}"
        )


def crawl_pages(
    urls: list[str],
    max_pages: int = 50,
    delay_seconds: float = 0.5
) -> list[CrawledPage]:
    """
    Crawl multiple website pages sequentially.

    Each page is processed independently.
    One failed page will not stop the entire crawl.
    """

    results = []

    unique_urls = list(dict.fromkeys(urls))

    urls_to_crawl = unique_urls[:max_pages]

    for index, url in enumerate(urls_to_crawl):

        print(
            f"Crawling {index + 1}/{len(urls_to_crawl)}: {url}"
        )

        result = fetch_page(url)

        results.append(result)

        if result.error:
            print(f"  FAILED: {result.error}")

        else:
            print(
                f"  SUCCESS: HTTP {result.status_code}"
            )

        if index < len(urls_to_crawl) - 1:
            time.sleep(delay_seconds)

    return results
