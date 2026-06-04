# Manga New Serial MVP

新連載候補を公式サイトから拾い、SQLiteに保存する個人用MVPです。

## できること

- 少年ジャンプ+トップページから「新連載」候補を抽出
- SQLiteに作品名・媒体・URL・検知日を保存
- 今週検知した新連載を表示
- メール送信用のHTMLレポートを生成

## セットアップ

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## 実行

```bash
python run.py
```

## DB確認

```bash
sqlite3 manga_watch.db "select * from works order by detected_at desc;"
```

## 次に足すもの

1. マガポケ取得
2. コミックDAYS取得
3. X言及数取得
4. 毎週月曜の自動実行
5. 4週間後追跡
