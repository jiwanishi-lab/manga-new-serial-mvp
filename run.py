from db import init_db, upsert_work, list_recent_works
from scrapers import scrape_all
from report import build_email_html
from mail import send_email
from google_trends import get_trend_score


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
        trend_score = get_trend_score(w["title"])

        enriched = dict(w)
        enriched["trend_score"] = trend_score
        enriched["start_date"] = w.get("start_date")
        enriched_works.append(enriched)

        print(
    f"- {w['title']} / "
    f"{w['platform']} / "
    f"開始日: {w.get('start_date')} / "
    f"Google Trends: {trend_score}"
)

    html = build_email_html(enriched_works)
    send_email("今週の新連載レポート", html)


if __name__ == "__main__":
    main()
