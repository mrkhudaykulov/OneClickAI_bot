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
```bash
cp .env.example .env
# Fill TELEGRAM_BOT_TOKEN and OPENAI_API_KEY
```
4) Run bot:
```bash
python -m bot.main
```

## Notes
- Uses OpenAI multimodal models (OPENAI_MODEL, default gpt-4o-mini)
- MediaPipe for pose overlay (CPU). OpenCV headless build is used.
- OCR/vision features call OpenAI Vision; control cost via prompts and limits.
