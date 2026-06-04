from datetime import datetime
from html import escape

def build_email_html(works):
    today = datetime.now().strftime("%Y/%m/%d")
    if not works:
        items = "<p>今週の新連載候補はまだ検知されていません。</p>"
    else:
        rows = []
        for i, w in enumerate(works, start=1):
            title = escape(w["title"])
            platform = escape(w["platform"])
            url = escape(w["url"] or "")
            link = f'<a href="{url}">{title}</a>' if url else title
            rows.append(f"""
            <tr>
              <td>{i}</td>
              <td>{link}</td>
              <td>{platform}</td>
              <td>未計測</td>
            </tr>
            """)
        items = f"""
        <table border="1" cellpadding="8" cellspacing="0">
          <tr>
            <th>#</th>
            <th>作品</th>
            <th>媒体</th>
            <th>SNS話題度</th>
          </tr>
          {''.join(rows)}
        </table>
        """

    return f"""
    <html>
      <body>
        <h2>🆕 今週の新連載レポート（{today}）</h2>
        <h3>新連載候補</h3>
        {items}
        <hr>
        <h3>🔥 4週間前の答え合わせ</h3>
        <p>次フェーズで実装します。</p>
      </body>
    </html>
    """
