from app.services.crawler.sitemap import discover_sitemap_urls
from app.services.crawler.browser_crawler import render_page
from app.services.crawler.extractor import extract_page
from app.services.chunker import chunk_page


BASE_URL = "https://www.mentormuni.com/"
MAX_PAGES = 19


def main():
    urls = discover_sitemap_urls(BASE_URL, max_pages=MAX_PAGES)

    total_pages = 0
    total_chunks = 0
    failed_pages = 0

    print(f"\nDiscovered URLs: {len(urls)}")
    print("=" * 90)

    for url in urls:
        try:
            rendered = render_page(url)

            if rendered.error or not rendered.html:
                failed_pages += 1
                print(f"FAILED: {url} | {rendered.error}")
                continue

            extracted = extract_page(rendered.url, rendered.html)

            if extracted.error or not extracted.content:
                failed_pages += 1
                print(f"EXTRACTION FAILED: {url}")
                continue

            chunks = chunk_page(
                extracted.url,
                extracted.title,
                extracted.content
            )

            total_pages += 1
            total_chunks += len(chunks)

            print(f"\nPAGE: {extracted.title}")
            print(f"URL: {url}")
            print(f"WORDS: {extracted.word_count}")
            print(f"CHUNKS: {len(chunks)}")
            print(
                "MAX CHUNK TOKENS:",
                max(chunk.token_count for chunk in chunks)
            )

        except Exception as exc:
            failed_pages += 1
            print(f"ERROR: {url} | {exc}")

    print("\n" + "=" * 90)
    print("FINAL SUMMARY")
    print("=" * 90)
    print(f"Discovered URLs : {len(urls)}")
    print(f"Processed pages : {total_pages}")
    print(f"Failed pages    : {failed_pages}")
    print(f"Total chunks    : {total_chunks}")


if __name__ == "__main__":
    main()