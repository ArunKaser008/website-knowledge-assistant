
from app.services.crawler.browser_crawler import render_page
from app.services.crawler.extractor import extract_page


TEST_URLS = [
    "https://www.mentormuni.com/",
    "https://www.mentormuni.com/how-it-works",
]


for url in TEST_URLS:
    print("\n" + "=" * 80)
    print("TESTING:", url)
    print("=" * 80)

    rendered = render_page(url)

    if rendered.error:
        print("RENDER ERROR:", rendered.error)
        continue

    extracted = extract_page(
        url=rendered.url,
        html=rendered.html,
        fallback_title=rendered.title,
    )

    print("TITLE:", extracted.title)
    print("WORD COUNT:", extracted.word_count)
    print("ERROR:", extracted.error)
    print("\nEXTRACTED CONTENT PREVIEW:\n")

    print(extracted.content[:2500])

    print("\n" + "-" * 80)
