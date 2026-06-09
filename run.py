print("DEBUG: run.py version = sort_by_start_date_v1")

from db import init_db, upsert_work, list_recent_works
from scrapers import scrape_all
from report import build_email_html
from mail import send_email
from google_trends import get_trend_score


def main():
    init_db()

    print("新連載候補を取得中...")
    items = scrape_all()

    print(f"DEBUG: scrape_all returned item_count={len(items)}")

    for item in items:
        print(
            "DEBUG: scraped item = "
            f"{item.get('title')} / "
            f"{item.get('platform')} / "
            f"{item.get('start_date')} / "
            f"{item.get('url')}"
        )

        upsert_work(
            title=item["title"],
            platform=item["platform"],
            url=item["url"],
            source=item["source"],
            start_date=item.get("start_date"),
        )

    works = list_recent_works(limit=20)

    print(f"{len(items)}件の候補を取得しました。")

    enriched_works = []

    for w in works:
        trend_score = get_trend_score(w["title"])

        enriched = dict(w)
        enriched["trend_score"] = trend_score
        enriched_works.append(enriched)

        print(
            f"- {enriched['title']} / "
            f"{enriched['platform']} / "
            f"開始日: {enriched.get('start_date')} / "
            f"Google Trends: {trend_score} / "
            f"{enriched['url']}"
        )

    enriched_works.sort(
        key=lambda x: x.get("start_date") or "",
        reverse=True,
    )

    html = build_email_html(enriched_works)
    send_email("今週の新連載レポート", html)


if __name__ == "__main__":
    main()
