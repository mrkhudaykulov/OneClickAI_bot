# OneClickAI_bot

Uzbek AI Telegram bot built with aiogram 3. Features:
- 📷 Photo services: calories estimation, dish recognition + recipe, OCR to text, product recognition
- 💪 Fitness: pose overlay (image), BMI calc, workout tips, simple plan

## Setup
1) Python 3.10+
2) Create virtualenv and install deps:
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
3) Configure env:
```
cp .env.example .env
# Fill TELEGRAM_BOT_TOKEN and OPENAI_API_KEY
# Optional admin/monetization settings:
# ADMIN_IDS=123456789,987654321
# MONETIZATION_CODE=secret123
```
4) Run bot:
```bash
python -m bot.main
```

## Notes
- Uses OpenAI multimodal models (OPENAI_MODEL, default gpt-4o-mini)
- MediaPipe for pose overlay (CPU). OpenCV headless build is used.
- OCR/vision features call OpenAI Vision; control cost via prompts and limits.

## Monetization & Limits
- Global toggle via admin command:
  - `/monet` (toggle), `/monet on`, `/monet off`
  - Non-admins can enable using `/monet <code>` if `MONETIZATION_CODE` is set
- Free credits are granted on first `/start` (default 20). Change defaults in DB `settings` table: `DEFAULT_FREE_CREDITS`, `GROUP_BONUS_CREDITS`.
- When limits end, users get CTA to Premium or to add the bot to a new group; adding to a new, previously unclaimed group grants 5 credits.
- Broadcast commands (admin only): `/broadcast_users <text>`, `/broadcast_groups <text>`
