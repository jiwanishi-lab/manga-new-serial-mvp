from datetime import datetime
from html import escape


def build_email_html(works):
    today = datetime.now().strftime("%Y/%m/%d")

    rows = []

    for i, w in enumerate(works, start=1):
        title = escape(w["title"])
        platform = escape(w["platform"])
        url = escape(w["url"] or "")
        start_date = w.get("start_date") or "不明"
        trend_score = w.get("trend_score", 0)

        link = f'<a href="{url}">{title}</a>' if url else title

        rows.append(f"""
        <tr>
          <td>{i}</td>
          <td>{link}</td>
          <td>{platform}</td>
          <td>{start_date}</td>
          <td>{trend_score}</td>
        </tr>
        """)

    items = f"""
    <table border="1" cellpadding="8" cellspacing="0">
      <tr>
        <th>#</th>
        <th>作品</th>
        <th>媒体</th>
        <th>開始日</th>
        <th>Google Trends / 直近7日</th>
      </tr>
      {''.join(rows)}
    </table>
    """

    return f"""
    <html>
      <body>
        <h2>🆕 今週の新連載レポート（{today}）</h2>
        <h3>新連載候補 + Google Trends</h3>
        {items}
        <hr>
        <h3>🔥 4週間前の答え合わせ</h3>
        <p>次フェーズで実装します。</p>
      </body>
    </html>
    """
