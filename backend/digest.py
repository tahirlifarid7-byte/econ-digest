#!/usr/bin/env python3
"""Free daily economy digest: Russian-language headlines from Google News RSS
(world business + Turkey economy) and lira rates from the Central Bank of Turkey.
Writes out/digest.json for the iOS app. No API keys, standard library only.

Usage: python3 digest.py
"""
import json
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

OUT = Path(__file__).parent / "out" / "digest.json"
UA = {"User-Agent": "Mozilla/5.0 (econ-digest)"}
GN = "https://news.google.com/rss"
GN_RU = "hl=ru&gl=RU&ceid=RU:ru"
WORLD_FEED = f"{GN}/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FuSjFHZ0pTVlNnQVAB?{GN_RU}"
TURKEY_QUERY = ("Турция (экономика OR лира OR инфляция OR ЦБ OR ставка OR экспорт OR бюджет OR биржа "
                "OR нефть OR газ OR инвестиции OR туризм OR цены) when:3d")
TURKEY_FEED = f"{GN}/search?q={urllib.parse.quote(TURKEY_QUERY)}&{GN_RU}"
ITEMS_PER_SECTION = 8
# Turkey search also returns politics; keep headlines that look economic
ECONOMY_WORDS = ("эконом", "лир", "инфляц", "банк", "ставк", "экспорт", "импорт", "ввп", "рын",
                 "бирж", "bist", "нефт", "газ", "резерв", "бюджет", "инвест", "туризм", "цен",
                 "курс", "доллар", "евро", "налог", "торгов", "долг", "рейтинг", "зарплат", "аэс")
MSK = timezone(timedelta(hours=3))  # Istanbul and Moscow are both UTC+3


def fetch(url: str) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as resp:
        return resp.read()


def news(url: str, keywords: tuple = ()) -> list[dict]:
    items, seen = [], set()
    for it in ET.fromstring(fetch(url)).iter("item"):
        title = (it.findtext("title") or "").strip()
        source = it.findtext("source") or None
        # Google News titles end with " - Source"
        if source and title.endswith(" - " + source):
            title = title[: -len(source) - 3]
        if not title or title.lower() in seen:
            continue
        if keywords and not any(k in title.lower() for k in keywords):
            continue
        seen.add(title.lower())
        try:
            published = parsedate_to_datetime(it.findtext("pubDate")).astimezone(MSK)
        except (TypeError, ValueError):
            published = None
        items.append({
            "title": title,
            "detail": published.strftime("%d.%m %H:%M") if published else "",
            "impact": None,
            "source": source,
            "url": it.findtext("link"),
            "_ts": published.timestamp() if published else 0,
        })
    items.sort(key=lambda i: i["_ts"], reverse=True)
    for i in items:
        del i["_ts"]
    return items[:ITEMS_PER_SECTION]


def section(url: str, keywords: tuple = ()) -> dict:
    items = news(url, keywords)
    summary = f"Главное: {items[0]['title']}" if items else "Новостей пока нет."
    return {"summary": summary, "items": items}


def indicators() -> list[dict]:
    result = []
    try:
        root = ET.fromstring(fetch("https://www.tcmb.gov.tr/kurlar/today.xml"))
        for code in ("USD", "EUR"):
            cur = root.find(f"Currency[@Kod='{code}']")
            rate = cur.findtext("ForexSelling") if cur is not None else None
            if rate:
                result.append({"name": f"{code}/TRY", "value": f"{float(rate):.2f}",
                               "change": f"ЦБ Турции, {root.get('Tarih')}"})
    except Exception as e:  # rates are optional; news still ships
        print(f"TCMB rates unavailable: {e}", file=sys.stderr)
    try:
        rates = json.loads(fetch("https://open.er-api.com/v6/latest/USD"))["rates"]
        result.append({"name": "EUR/USD", "value": f"{1 / rates['EUR']:.4f}", "change": None})
        if "RUB" in rates:
            result.append({"name": "USD/RUB", "value": f"{rates['RUB']:.2f}", "change": None})
    except Exception as e:
        print(f"FX rates unavailable: {e}", file=sys.stderr)
    return result


def main() -> int:
    now = datetime.now(MSK)
    digest = {
        "date": now.strftime("%d.%m.%Y"),
        "generated_at": now.isoformat(),
        "indicators": indicators(),
        "world": section(WORLD_FEED),
        "turkey": section(TURKEY_FEED, ECONOMY_WORDS),
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(digest, ensure_ascii=False, indent=2))
    print(f"Wrote {OUT}: {len(digest['world']['items'])} world, "
          f"{len(digest['turkey']['items'])} Turkey, {len(digest['indicators'])} indicators")
    return 0


if __name__ == "__main__":
    sys.exit(main())
