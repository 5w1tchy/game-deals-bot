# 🎮 Game Deals Discord Bot

A Discord bot that posts:
- 🗓️ Upcoming monthly PC game releases (via Game Informer & Steam)
- 🎁 Weekly Epic Games Store freebies
- 🔥 Good & bad Steam deals (based on reviews and discounts)

---

## 📦 Features

- Posts to Discord:
  - 🗓️ Monthly PC releases from Game Informer
  - 🎁 Epic Games weekly freebies
  - 🔥 Steam deals with review/discount filters
- Auto-cleans channels before posting
- Rich embeds with:
  - Cover image
  - Release date
  - Description
  - Price

---

## 🔧 Setup

### 1. Clone and enter the project

```bash
git clone https://github.com/yourusername/game-deals-bot.git
cd game-deals-bot
```

### 2. Create a virtual environment and install requirements

```bash
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

### 3. Create your config

Make a file called `config.py` and add this:

```py
DISCORD_TOKEN = "your-bot-token"
TARGET_HOUR_UTC = 15  # Hour (UTC) to post weekly Epic freebies
FREE_CHANNEL = 123456789012345678  # Epic freebies channel ID
MONTHLY_RELEASES_CHANNEL = 123456789012345678  # Monthly posts channel ID
LOG_CHANNEL_ID = 123456789012345678  # Where errors get posted (optional)
```

### 4. Run the bot

```bash
python bot.py
```

---

## 📂 Project Structure

```
game-deals-bot/
│
├── bot.py                   # Entry point
├── commands.py              # All bot commands (!monthly, !deals, etc.)
├── config.py                # Your token and channel IDs
│
├── scrapers/                # Game Informer, Steam, and Epic data fetchers
├── tasks/                   # Scheduled loops (daily, weekly, monthly)
├── utils/                   # JSON, date, and Steam helpers
│
├── data/                    # JSON state tracking files
├── requirements.txt
├── README.md
```

---

## 🧠 Notes

- Epic data uses their official backend API
- Monthly Steam info (price, image, desc) is scraped from the store
- Bot auto-deletes previous messages in deal/freebie channels (except pinned)
