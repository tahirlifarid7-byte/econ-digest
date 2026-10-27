#!/usr/bin/env python3
"""Daily economy digest agent: asks Claude (with web search) for today's world and
Turkey economy news and writes out/digest.json for the iOS app.

Paid variant (needs Anthropic API credits). The free daily digest is digest.py.

Usage: ANTHROPIC_API_KEY=sk-ant-... python3 digest_ai.py
"""
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

MODEL = os.environ.get("DIGEST_MODEL", "claude-sonnet-5-5")
OUT = Path(__file__).parent / "out" / "digest.json"

PROMPT = """Сегодня {today}. Найди через веб-поиск самые важные экономические события за последние 24-48 часов:
1) в мире (центробанки и ставки, инфляция, рынки, нефть/газ/золото, торговля и тарифы, крупные экономики);
2) в Турции (решения TCMB, инфляция TÜİK, курс лиры, BIST 100, внешняя торговля, бюджет, рейтинги, реформы).

Правила: только факты из найденных источников, ничего не выдумывай. Если данных нет, пиши null.
Пиши по-русски, кратко и по делу. 5-7 новостей на раздел.

Верни ТОЛЬКО JSON без пояснений и markdown, строго такой формы:
{{
  "date": "{today}",
  "indicators": [{{"name": "USD/TRY", "value": "строка", "change": "строка или null"}}],
  "world":  {{"summary": "2-3 предложения о главном", "items": [{{"title": "", "detail": "1-2 предложения", "impact": "positive|negative|neutral", "source": "название издания", "url": "https://..."}}]}},
  "turkey": {{"summary": "...", "items": [ ...как выше... ]}}
}}
В indicators включи, если нашёл: USD/TRY, EUR/TRY, BIST 100, Brent, золото, ключевая ставка TCMB, ставка ФРС."""


def call_claude(api_key: str, today: str) -> str:
    body = {
        "model": MODEL,
        "max_tokens": 6000,
        "tools": [{"type": "web_search_20250305", "name": "web_search", "max_uses": 8}],
        "messages": [{"role": "user", "content": PROMPT.format(today=today)}],
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode(),
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Anthropic API error {e.code}: {e.read().decode()}")
    return "".join(b.get("text", "") for b in data["content"] if b["type"] == "text")


def extract_json(text: str) -> dict:
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("no JSON object in model reply:\n" + text[:500])
    return json.loads(text[start : end + 1])


def main() -> int:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Set ANTHROPIC_API_KEY", file=sys.stderr)
        return 1
    today = datetime.now().strftime("%Y-%m-%d")
    digest = extract_json(call_claude(api_key, today))
    digest["generated_at"] = datetime.now(timezone.utc).isoformat()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(digest, ensure_ascii=False, indent=2))
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
