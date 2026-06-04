import re
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 manga-new-serial-mvp/0.1"
}

def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text

def guess_title_from_text(text: str) -> str | None:
    """
    ジャンプ+トップのような表示から作品名っぽい部分を拾う簡易ロジック。
    例:
      "[第1話]ルノリータ 棉きのし"
      "明治時代にネット開通!! 世界を繋ぎ尽くすインターネット巫女 コガッツオ/木野イチカ 新連載"
    """
    text = clean_text(text)
    if not text:
        return None

    # [第1話]タイトル 作者 のパターン
    m = re.search(r"\[(?:第)?1話\]\s*([^ ]+)", text)
    if m:
        return m.group(1).strip("「」『』[] ")

    # 「新連載」の直前周辺を使う
    if "新連載" in text:
        before = text.split("新連載")[0].strip()
        parts = before.split()
        # 作者名らしき最後の1要素を落とし、直前の塊をタイトル候補にする
        if len(parts) >= 2:
            return parts[-2].strip("「」『』[] ")
        if parts:
            return parts[-1].strip("「」『』[] ")

    return None

def scrape_jump_plus():
    """
    少年ジャンプ+トップから「新連載」または「[第1話]」を含むリンク周辺を候補として抽出。
    公式トップには新連載枠や第1話リンクが表示されるため、MVPではここから拾う。
    """
    url = "https://shonenjumpplus.com/"
    res = requests.get(url, headers=HEADERS, timeout=20)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")
    candidates = {}

    for a in soup.find_all("a"):
        text = clean_text(a.get_text(" "))
        href = a.get("href")
        if not text:
            continue

        if ("新連載" in text) or ("[第1話]" in text) or ("[1話]" in text):
            title = guess_title_from_text(text)
            if title and len(title) >= 2:
                candidates[title] = {
                    "title": title,
                    "platform": "少年ジャンプ+",
                    "url": urljoin(url, href) if href else url,
                    "source": "shonenjumpplus_top",
                    "raw_text": text,
                }

    return list(candidates.values())

def scrape_all():
    results = []
    results.extend(scrape_jump_plus())
    return results
