from app.services.crawler.sitemap import discover_sitemap_urls


if __name__ == "__main__":

    website_url = "https://www.mentormuni.com"

    urls = discover_sitemap_urls(
        website_url=website_url,
        max_pages=50
    )

    print(f"\nTotal URLs discovered: {len(urls)}")

    for index, url in enumerate(urls, start=1):
        print(f"{index}. {url}")