import re
from datetime import datetime, timedelta
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 manga-new-serial-mvp/0.1"
}

RECENT_DAYS = 7


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text


def normalize_date(year: str, month: str, day: str) -> str:
    return f"{year}/{int(month):02d}/{int(day):02d}"


def extract_date_from_text(text: str) -> str | None:
    text = clean_text(text)

    m = re.search(r"(20\d{2})年(\d{1,2})月(\d{1,2})日", text)
    if m:
        return normalize_date(*m.groups())

    m = re.search(r"(20\d{2})/(\d{1,2})/(\d{1,2})", text)
    if m:
        return normalize_date(*m.groups())

    m = re.search(r"(20\d{2})-(\d{1,2})-(\d{1,2})", text)
    if m:
        return normalize_date(*m.groups())

    return None


def is_recent_date(date_text: str | None, days: int = RECENT_DAYS) -> bool:
    if not date_text:
        return False

    try:
        target = datetime.strptime(date_text, "%Y/%m/%d")
        cutoff = datetime.now() - timedelta(days=days)
        return target >= cutoff
    except Exception:
        return False


def fetch_text(url: str) -> str:
    res = requests.get(url, headers=HEADERS, timeout=20)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    return soup.get_text(" ")


def guess_title_from_text(text: str) -> str | None:
    text = clean_text(text)
    if not text:
        return None

    m = re.search(r"\[(?:第)?1話\]\s*([^ ]+)", text)
    if m:
        return m.group(1).strip("「」『』[] ")

    if "新連載" in text:
        before = text.split("新連載")[0].strip()
        parts = before.split()
        if len(parts) >= 2:
            return parts[-2].strip("「」『』[] ")
        if parts:
            return parts[-1].strip("「」『』[] ")

    return None


def get_episode_date(url: str) -> str | None:
    try:
        return extract_date_from_text(fetch_text(url))
    except Exception as e:
        print(f"開始日取得失敗: {url} / {e}")

    return None


def scrape_jump_plus():
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
            episode_url = urljoin(url, href) if href else url

            if title and len(title) >= 2:
                start_date = get_episode_date(episode_url)

                if not is_recent_date(start_date):
                    continue

                candidates[title] = {
                    "title": title,
                    "platform": "少年ジャンプ+",
                    "url": episode_url,
                    "source": "shonenjumpplus_top",
                    "raw_text": text,
                    "start_date": start_date,
                }

    print(f"DEBUG: 少年ジャンプ+ result_count={len(candidates)}")

    return list(candidates.values())


def guess_comic_days_title(text: str) -> str | None:
    text = clean_text(text)
    if not text:
        return None

    remove_words = [
        "新作",
        "話題作",
        "無料",
        "毎週",
        "隔週",
        "月曜更新",
        "火曜更新",
        "水曜更新",
        "木曜更新",
        "金曜更新",
        "土曜更新",
        "日曜更新",
    ]

    for word in remove_words:
        text = text.replace(word, " ")

    text = clean_text(text)
    parts = text.split()

    if parts:
        return parts[0].strip("「」『』[] ")

    return None


def get_comic_days_start_date(url: str) -> str | None:
    try:
        return extract_date_from_text(fetch_text(url))
    except Exception as e:
        print(f"コミックDAYS開始日取得失敗: {url} / {e}")

    return None


def scrape_comic_days():
    print("DEBUG: コミックDAYS取得開始")

    url = "https://comic-days.com/pickup"
    res = requests.get(url, headers=HEADERS, timeout=20)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")
    all_links = soup.find_all("a")

    candidates = {}

    for a in all_links:
        text = clean_text(a.get_text(" "))
        href = a.get("href")

        if not text or not href:
            continue

        if "新作" not in text:
            continue

        title = guess_comic_days_title(text)
        work_url = urljoin(url, href)

        if title and len(title) >= 2:
            start_date = get_comic_days_start_date(work_url)

            if not is_recent_date(start_date):
                continue

            candidates[title] = {
                "title": title,
                "platform": "コミックDAYS",
                "url": work_url,
                "source": "comic_days_pickup",
                "raw_text": text,
                "start_date": start_date,
            }

    print(f"DEBUG: コミックDAYS result_count={len(candidates)}")

    return list(candidates.values())


def guess_magapoke_title(text: str) -> str | None:
    text = clean_text(text)
    if not text:
        return None

    remove_phrases = [
        "最新話更新",
        "最新単行本",
        "話分無料",
        "巻発売中",
        "毎週",
        "隔週",
        "毎月",
        "日前後",
    ]

    for phrase in remove_phrases:
        if phrase in text:
            text = text.split(phrase)[0].strip()

    parts = text.split()
    if parts:
        return parts[0].strip("「」『』[] ")

    return None


def get_magapoke_start_date(url: str) -> str | None:
    try:
        text = fetch_text(url)

        # 作品ページに日付があれば拾う
        date = extract_date_from_text(text)
        if date:
            return date

    except Exception as e:
        print(f"マガポケ開始日取得失敗: {url} / {e}")

    return None


def scrape_magapoke():
    print("DEBUG: マガポケ取得開始")

    url = "https://pocket.shonenmagazine.com/ranking/31"
    res = requests.get(url, headers=HEADERS, timeout=20)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")
    candidates = {}

    for a in soup.find_all("a"):
        text = clean_text(a.get_text(" "))
        href = a.get("href")

        if not text or not href:
            continue

        # ランキング内の作品リンクっぽいものだけ拾う
        if "最新話更新" not in text:
            continue

        title = guess_magapoke_title(text)
        work_url = urljoin(url, href)

        if title and len(title) >= 2:
            start_date = get_magapoke_start_date(work_url)

            if not is_recent_date(start_date):
                continue

            candidates[title] = {
                "title": title,
                "platform": "マガポケ",
                "url": work_url,
                "source": "magapoke_ranking_31",
                "raw_text": text,
                "start_date": start_date,
            }

    print(f"DEBUG: マガポケ result_count={len(candidates)}")

    return list(candidates.values())


def scrape_all():
    results = []

    jump_plus_results = scrape_jump_plus()
    print(f"DEBUG: scrape_all 少年ジャンプ+={len(jump_plus_results)}")
    results.extend(jump_plus_results)

    comic_days_results = scrape_comic_days()
    print(f"DEBUG: scrape_all コミックDAYS={len(comic_days_results)}")
    results.extend(comic_days_results)

    magapoke_results = scrape_magapoke()
    print(f"DEBUG: scrape_all マガポケ={len(magapoke_results)}")
    results.extend(magapoke_results)

    print(f"DEBUG: scrape_all total={len(results)}")

    return results
