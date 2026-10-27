# Экономика: мир и Турция (iOS)

- `backend/digest.py` — бесплатный агент: новости Google News (RSS, по-русски) + курсы ЦБ Турции, пишет `backend/out/digest.json`.
- `backend/digest_ai.py` — платный вариант с Claude и веб-поиском (нужен баланс Anthropic API).
- `EconDigest/` — SwiftUI-приложение (iOS 17+): вкладки «Мир» и «Турция», pull-to-refresh, кэш, настройка URL.

## Запуск
1. `python3 backend/digest.py`
2. `cd backend/out && python3 -m http.server 8000`
3. Открыть `EconDigest/EconDigest.xcodeproj` в Xcode, выбрать свою Team, запустить.
   На реальном iPhone в настройках приложения укажите `http://<IP-вашего-Mac>:8000/digest.json`.

## Каждый день
Запускайте digest.py по расписанию (cron / launchd / GitHub Actions) и отдавайте digest.json с любого хостинга.
