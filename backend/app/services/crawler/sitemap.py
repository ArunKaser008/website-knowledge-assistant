"""Sitemap parsing and URL discovery."""

import gzip
import xml.etree.ElementTree as ET

from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen


USER_AGENT = "WebsiteKnowledgeAssistant/1.0"

MAX_SITEMAPS = 20
MAX_RESPONSE_SIZE = 5 * 1024 * 1024


def normalize_url(url: str) -> str | None:
    """
    Validate and normalize HTTP/HTTPS URLs.
    Remove fragments and reject invalid URLs.
    """

    try:
        parsed = urlsplit(url.strip())

        if parsed.scheme not in ("http", "https"):
            return None

        if not parsed.hostname or parsed.username or parsed.password:
            return None

        return urlunsplit((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path or "/",
            parsed.query,
            ""
        ))

    except ValueError:
        return None


def is_same_website(url: str, website_url: str) -> bool:
    """
    Ensure discovered URLs belong to the same website.
    www and non-www versions are treated as equivalent.
    """

    target_host = urlsplit(url).hostname
    website_host = urlsplit(website_url).hostname

    if not target_host or not website_host:
        return False

    target_host = target_host.lower().removeprefix("www.")
    website_host = website_host.lower().removeprefix("www.")

    return target_host == website_host


def fetch_url(url: str) -> bytes | None:
    """
    Fetch website content with a timeout and response-size limit.
    """

    request = Request(
        url,
        headers={"User-Agent": USER_AGENT}
    )

    try:
        with urlopen(request, timeout=15) as response:
            content = response.read(MAX_RESPONSE_SIZE + 1)

            if len(content) > MAX_RESPONSE_SIZE:
                return None

            if urlsplit(response.geturl()).scheme not in ("http", "https"):
                return None

            return content

    except (HTTPError, URLError, TimeoutError, OSError, ValueError):
        return None


def discover_robots_sitemaps(website_url: str) -> list[str]:
    """
    Extract sitemap locations declared in robots.txt.
    """

    robots_url = urljoin(website_url, "/robots.txt")

    content = fetch_url(robots_url)

    if not content:
        return []

    sitemaps = []

    for line in content.decode("utf-8", errors="ignore").splitlines():

        line = line.strip()

        if line.lower().startswith("sitemap:"):

            sitemap_url = line.split(":", 1)[1].strip()

            normalized = normalize_url(sitemap_url)

            if normalized and is_same_website(normalized, website_url):
                sitemaps.append(normalized)

    return sitemaps


def parse_sitemap(content: bytes) -> tuple[str, list[str]]:
    """
    Parse XML sitemap content.

    Returns:
        sitemap_type: index or urlset
        locations: URLs found inside the sitemap
    """

    if content[:2] == b"\x1f\x8b":
        content = gzip.decompress(content)

    root = ET.fromstring(content)

    root_tag = root.tag.split("}")[-1].lower()

    locations = []

    for element in root.iter():

        if element.tag.split("}")[-1].lower() == "loc":

            if element.text:
                locations.append(element.text.strip())

    return root_tag, locations


def discover_sitemap_urls(
    website_url: str,
    max_pages: int = 50
) -> list[str]:
    """
    Discover website URLs using robots.txt and XML sitemaps.

    Supports:
        - Sitemap index files
        - Regular XML sitemaps
        - Gzipped sitemaps

    Returns a unique list of same-website URLs.
    """

    website_url = normalize_url(website_url)

    if not website_url:
        raise ValueError("Invalid website URL")

    sitemap_queue = discover_robots_sitemaps(website_url)

    # Add common sitemap locations as fallbacks.
    sitemap_queue.extend([
        urljoin(website_url, "/sitemap.xml"),
        urljoin(website_url, "/sitemap_index.xml")
    ])

    visited_sitemaps = set()
    discovered_urls = []
    discovered_set = set()

    while sitemap_queue and len(visited_sitemaps) < MAX_SITEMAPS:

        sitemap_url = sitemap_queue.pop(0)

        if sitemap_url in visited_sitemaps:
            continue

        visited_sitemaps.add(sitemap_url)

        content = fetch_url(sitemap_url)

        if not content:
            continue

        try:
            sitemap_type, locations = parse_sitemap(content)

        except (ET.ParseError, ValueError, OSError):
            continue

        for location in locations:

            normalized_url = normalize_url(
                urljoin(sitemap_url, location)
            )

            if not normalized_url:
                continue

            if not is_same_website(normalized_url, website_url):
                continue

            if sitemap_type == "sitemapindex":

                if normalized_url not in visited_sitemaps:
                    sitemap_queue.append(normalized_url)

            elif sitemap_type == "urlset":

                if normalized_url not in discovered_set:

                    discovered_set.add(normalized_url)
                    discovered_urls.append(normalized_url)

                    if len(discovered_urls) >= max_pages:
                        return discovered_urls

    return discovered_urls
