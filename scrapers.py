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
        res = requests.get(url, headers=HEADERS, timeout=20)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, "html.parser")
        text = soup.get_text(" ")

        return extract_date_from_text(text)

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
        res = requests.get(url, headers=HEADERS, timeout=20)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, "html.parser")
        text = soup.get_text(" ")

        return extract_date_from_text(text)

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

    print(f"DEBUG: コミックDAYS aタグ数={len(all_links)}")

    candidates = {}
    checked_count = 0
    new_word_count = 0

    for a in all_links:
        text = clean_text(a.get_text(" "))
        href = a.get("href")

        if not text or not href:
            continue

        checked_count += 1

        if "新作" in text:
            new_word_count += 1
            print(f"DEBUG: コミックDAYS新作候補: {text[:120]} / {href}")

            title = guess_comic_days_title(text)
            work_url = urljoin(url, href)

            if title and len(title) >= 2:
                start_date = get_comic_days_start_date(work_url)

                candidates[title] = {
                    "title": title,
                    "platform": "コミックDAYS",
                    "url": work_url,
                    "source": "comic_days_pickup",
                    "raw_text": text,
                    "start_date": start_date,
                }

    print(
        "DEBUG: コミックDAYS "
        f"checked_count={checked_count}, "
        f"new_word_count={new_word_count}, "
        f"result_count={len(candidates)}"
    )

    return list(candidates.values())


def scrape_all():
    results = []

    jump_plus_results = scrape_jump_plus()
    print(f"DEBUG: scrape_all 少年ジャンプ+={len(jump_plus_results)}")
    results.extend(jump_plus_results)

    comic_days_results = scrape_comic_days()
    print(f"DEBUG: scrape_all コミックDAYS={len(comic_days_results)}")
    results.extend(comic_days_results)

    print(f"DEBUG: scrape_all total={len(results)}")

    return results
