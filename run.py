from db import init_db, upsert_work, list_recent_works
from scrapers import scrape_all
from report import build_email_html
from mail import send_email
from x_counts import get_x_post_count


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

    enriched_works = []

    for w in works:
        x_count = get_x_post_count(w["title"])

        enriched = dict(w)
        enriched["x_post_count"] = x_count
        enriched_works.append(enriched)

        print(
            f"- {w['title']} / "
            f"{w['platform']} / "
            f"X投稿数: {x_count} / "
            f"{w['url']}"
        )

    html = build_email_html(enriched_works)
    send_email("今週の新連載レポート", html)


if __name__ == "__main__":
    main()
