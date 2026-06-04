from pytrends.request import TrendReq


def get_trend_score(keyword: str) -> int:
    try:
        pytrends = TrendReq(hl="ja-JP", tz=540)

        pytrends.build_payload(
            [keyword],
            timeframe="now 7-d",
            geo="JP",
        )

        df = pytrends.interest_over_time()

        if df.empty or keyword not in df.columns:
            return 0

        return int(df[keyword].mean())

    except Exception as e:
        print(f"Google Trends取得失敗: {keyword} / {e}")
        return 0
