from db import init_db, upsert_work, list_recent_works
from scrapers import scrape_all
from report import build_email_html
from mail import send_email

def main():
    init_db()

    print("新連載候補を取得中...")
    items = scrape_all()

    for item in items:
        upsert_work(
            title=item["title"],
            platform=item["platform"],
            url=item["url"],
            source=item["source"],
        )

    works = list_recent_works(limit=20)

    print(f"{len(items)}件の候補を取得しました。")
    for w in works:
        print(f"- {w['title']} / {w['platform']} / {w['url']}")

    html = build_email_html(works)
    send_email("今週の新連載レポート", html)

if __name__ == "__main__":
    main()
