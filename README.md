# 🌤️ DayMate — Your AI-Powered Daily Companion

> Built for the OpenClaw Challenge 2026 | by Harshavardhan Mulavagili

DayMate is an autonomous AI agent built on OpenClaw that does two things brilliantly:

1. **📰 Morning News Briefing** — Tell it your interests once. Every morning at 8am, it fetches the latest headlines, summarises them into 5 clear bullets using AI, and delivers them straight to your Telegram.
2. **🧾 Instant Bill Splitting** — Send a photo of any restaurant bill. DayMate reads it using vision AI, asks how many people, adds tip if you want, and tells everyone exactly what they owe.

No apps to open. No subscriptions. Just your Telegram.

---

## 🎯 The Problem It Solves

Every day, two genuinely annoying things happen to millions of people:

- You wake up and spend 20 minutes scrolling through noise to find news that actually matters to you
- You finish a meal with friends and someone has to awkwardly do maths on their phone while everyone waits

DayMate eliminates both. Permanently.

---

## 🏗️ How It Works
User (Telegram) → OpenClaw Agent → Python Logic → Groq AI → Reply
**Morning Briefing Flow:**
1. OpenClaw scheduler triggers at 8am daily
2. `news.py` fetches top headlines from NewsAPI matching user interests
3. Groq AI (Llama 3) summarises into a friendly 5-bullet briefing
4. OpenClaw delivers it via Telegram automatically

**Bill Splitting Flow:**
1. User sends bill photo to Telegram
2. OpenClaw receives the image and triggers `bills.py`
3. Groq Vision AI reads all items and prices from the photo
4. User inputs number of people + optional tip
5. DayMate calculates and returns each person's exact share

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Agent Framework | OpenClaw 2026 |
| Messaging | Telegram Bot API |
| AI / LLM | Groq API (Llama 3) |
| Vision AI | Groq Vision (Llama 3.2) |
| News Data | NewsAPI.org |
| Language | Python 3.11 |
| Scheduling | OpenClaw scheduler + schedule |

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/harsha1803/daymate.git
cd daymate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
Create a `.env` file:
TELEGRAM_TOKEN=your_telegram_bot_token
NEWS_API_KEY=your_newsapi_key
GROQ_API_KEY=your_groq_api_key
### 4. Run with OpenClaw
```bash
openclaw run openclaw.json
```

Or run directly:
```bash
python bot.py
```

### 5. Open Telegram and message your bot
- Send `/start` to begin
- Send `/news` to set your interests and get your first briefing
- Send any bill photo to split it instantly

---

## 📁 Project Structure
daymate/
├── bot.py              # Main OpenClaw agent entry point
├── news.py             # News fetching and AI summarisation
├── bills.py            # Bill photo reading and splitting
├── openclaw.json       # OpenClaw agent configuration
├── requirements.txt    # Python dependencies
├── .env                # API keys (not committed)
└── README.md           # This file
---

## 💡 Why OpenClaw?

OpenClaw's scheduling and Telegram integration made it possible to build a truly autonomous agent — one that acts without being asked. The morning briefing doesn't wait for the user to open an app. It just arrives. That's the power of an agent versus a chatbot.

---

## 🔑 Getting Your API Keys

| Key | Where to get it | Cost |
|-----|----------------|------|
| Telegram Token | @BotFather on Telegram | Free |
| NewsAPI Key | newsapi.org/register | Free |
| Groq API Key | console.groq.com | Free |

---

*Made with ❤️ in Glasgow, Scotland*