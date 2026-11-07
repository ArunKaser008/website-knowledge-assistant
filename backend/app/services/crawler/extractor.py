
import re
from dataclasses import dataclass
from typing import Optional

from bs4 import BeautifulSoup, Tag


@dataclass
class ExtractedPage:
    url: str
    title: str
    content: str
    word_count: int
    error: Optional[str] = None


UNWANTED_TAGS = [
    "script",
    "style",
    "noscript",
    "svg",
    "iframe",
    "canvas",
    "header",
    "footer",
    "nav",
    "aside",
    "form",
    "button",
]

UNWANTED_SELECTORS = [
    "[aria-hidden='true']",
    "[hidden]",
    "[role='dialog']",
    "[role='alertdialog']",
    ".cookie-banner",
    ".cookie-consent",
    ".cookie-popup",
    ".newsletter-popup",
    ".modal",
    ".advertisement",
    ".ads",
]

CONTENT_TAGS = [
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "p",
    "li",
    "blockquote",
    "td",
    "th",
]


def clean_text(text: str) -> str:
    """Normalize whitespace while preserving meaningful punctuation."""

    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s*\n\s*", "\n", text)

    return text.strip()


def extract_title(soup: BeautifulSoup) -> str:
    """Extract the page title."""

    if soup.title:
        title = soup.title.get_text(" ", strip=True)

        if title:
            return clean_text(title)

    heading = soup.find("h1")

    if heading:
        return clean_text(heading.get_text(" ", strip=True))

    return ""


def extract_main_content(soup: BeautifulSoup) -> Tag:
    """Identify the main content container."""

    selectors = [
        "main",
        "article",
        "[role='main']",
        "#main",
        "#content",
        ".main-content",
        ".page-content",
    ]

    for selector in selectors:
        element = soup.select_one(selector)

        if element:
            return element

    return soup.body or soup


def extract_content(html: str) -> str:
    """Extract meaningful text without parent-child duplication."""

    if not html or not html.strip():
        return ""

    soup = BeautifulSoup(html, "html.parser")

    for tag_name in UNWANTED_TAGS:
        for element in soup.find_all(tag_name):
            element.decompose()

    for selector in UNWANTED_SELECTORS:
        for element in soup.select(selector):
            element.decompose()

    content_root = extract_main_content(soup)

    extracted_lines = []
    seen_lines = set()

    for element in content_root.find_all(CONTENT_TAGS):

        # Skip parent elements when nested content elements exist.
        # Their children will be extracted separately.
        if element.find(CONTENT_TAGS):
            continue

        text = clean_text(element.get_text(" ", strip=True))

        if not text:
            continue

        # Remove repeated text while preserving original order.
        normalized = re.sub(r"\s+", " ", text).strip().casefold()

        if normalized in seen_lines:
            continue

        seen_lines.add(normalized)
        extracted_lines.append(text)

    # Fallback for pages without standard content elements.
    if not extracted_lines:
        fallback_text = clean_text(
            content_root.get_text(" ", strip=True)
        )

        if fallback_text:
            extracted_lines.append(fallback_text)

    return "\n".join(extracted_lines)


def extract_page(
    url: str,
    html: str,
    fallback_title: str = "",
) -> ExtractedPage:
    """Extract page metadata and clean content."""

    if not html or not html.strip():
        return ExtractedPage(
            url=url,
            title=fallback_title,
            content="",
            word_count=0,
            error="HTML content is empty",
        )

    soup = BeautifulSoup(html, "html.parser")

    title = extract_title(soup) or fallback_title
    content = extract_content(html)

    if not content:
        return ExtractedPage(
            url=url,
            title=title,
            content="",
            word_count=0,
            error="No meaningful page content found",
        )

    return ExtractedPage(
        url=url,
        title=title,
        content=content,
        word_count=len(content.split()),
    )
