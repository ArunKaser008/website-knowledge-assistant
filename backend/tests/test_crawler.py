
from app.services.crawler.sitemap import discover_sitemap_urls
from app.services.crawler.crawler import crawl_pages


if __name__ == "__main__":

    website_url = "https://www.mentormuni.com"

    # Step 1: Discover website URLs
    urls = discover_sitemap_urls(
        website_url=website_url,
        max_pages=50
    )

    print(f"\nDiscovered URLs: {len(urls)}")

    # Step 2: Crawl website pages
    pages = crawl_pages(
        urls=urls,
        max_pages=50,
        delay_seconds=0.5
    )

    # Step 3: Display crawl statistics
    successful = sum(
        1 for page in pages
        if page.html is not None
    )

    failed = len(pages) - successful

    print("\n========== CRAWL SUMMARY ==========")
    print(f"Total pages : {len(pages)}")
    print(f"Successful  : {successful}")
    print(f"Failed      : {failed}")

    # Step 4: Display extracted HTML size
    for page in pages:

        html_size = (
            len(page.html)
            if page.html
            else 0
        )

        print(
            f"{page.url} | "
            f"Status: {page.status_code} | "
            f"HTML Size: {html_size} characters"
        )
