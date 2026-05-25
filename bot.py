import os
import logging
import schedule
import time
import threading
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)
from dotenv import load_dotenv
from news import get_morning_briefing
from bills import read_bill, split_bill

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

WAITING_FOR_INTERESTS = 1
WAITING_FOR_PEOPLE = 2
WAITING_FOR_TIP = 3

user_interests = {}
user_bill_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    await update.message.reply_text(
        f"👋 Hey {user}! I'm *DayMate* 🌤️\n\n"
        f"Your AI-powered daily companion!\n\n"
        f"📰 /news — Set interests & get morning briefings\n"
        f"🧾 Send a *bill photo* — I'll split it instantly\n"
        f"ℹ️ /help — Show this menu again\n\n"
        f"Try /news first 🚀",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌤️ *DayMate Commands*\n\n"
        "📰 /news — Set interests & get your briefing\n"
        "🧾 Send a photo — Split any restaurant bill\n"
        "📅 /briefing — Get today's news right now\n\n"
        "Built with ❤️ using OpenClaw",
        parse_mode="Markdown"
    )

async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📰 *News Briefing Setup*\n\n"
        "What topics are you interested in?\n\n"
        "Examples:\n"
        "• AI, technology, football\n"
        "• Scottish news, business, science\n\n"
        "Just type your interests below 👇",
        parse_mode="Markdown"
    )
    return WAITING_FOR_INTERESTS

async def save_interests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    interests = update.message.text
    user_interests[user_id] = interests
    await update.message.reply_text(
        f"✅ Got it! Briefing you on: *{interests}*\n\n⏳ Fetching now...",
        parse_mode="Markdown"
    )
    briefing = get_morning_briefing(interests)
    await update.message.reply_text(briefing)
    await update.message.reply_text("⏰ You'll get this every morning at 8am!\nSend a bill photo anytime 🧾")
    return ConversationHandler.END

async def briefing_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_interests:
        await update.message.reply_text("⚠️ Set your interests first with /news")
        return
    await update.message.reply_text("⏳ Fetching your briefing...")
    briefing = get_morning_briefing(user_interests[user_id])
    await update.message.reply_text(briefing)   
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text("🧾 Got your bill photo! Reading it now...")
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    file_path = f"bill_{user_id}.jpg"
    await file.download_to_drive(file_path)
    bill_text = read_bill(file_path)
    if not bill_text or "UNREADABLE" in bill_text:
        await update.message.reply_text("❌ Couldn't read the bill clearly. Try a clearer photo!")
        return
    user_bill_data[user_id] = bill_text
    await update.message.reply_text(
        "✅ Bill read!\n\n👥 How many people splitting this?\nType a number (e.g. 3)"
    )
    return WAITING_FOR_PEOPLE

async def get_num_people(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        num_people = int(update.message.text.strip())
        if num_people < 2:
            await update.message.reply_text("Please enter 2 or more!")
            return WAITING_FOR_PEOPLE
        context.user_data["num_people"] = num_people
        await update.message.reply_text(
            f"👍 Splitting between {num_people} people!\n\n"
            f"💰 Add a tip? Type percentage (e.g. 10)\nOr 0 for no tip"
        )
        return WAITING_FOR_TIP
    except ValueError:
        await update.message.reply_text("Please type a valid number!")
        return WAITING_FOR_PEOPLE

async def get_tip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        tip = int(update.message.text.strip())
        num_people = context.user_data["num_people"]
        bill_text = user_bill_data[user_id]
        await update.message.reply_text("⏳ Calculating your split...")
        result = split_bill(bill_text, num_people, tip)
        await update.message.reply_text(result, parse_mode="Markdown")
        try:
            os.remove(f"bill_{user_id}.jpg")
        except:
            pass
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Please type a valid number!")
        return WAITING_FOR_TIP

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled. Send /start to begin again.")
    return ConversationHandler.END

def send_morning_briefings(app):
    async def send_all():
        for user_id, interests in user_interests.items():
            try:
                briefing = get_morning_briefing(interests)
                await app.bot.send_message(
                    chat_id=user_id,
                    text=f"⏰ *Good Morning! Your DayMate Briefing:*\n\n{briefing}",
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.error(f"Failed to send to {user_id}: {e}")
    import asyncio
    asyncio.run(send_all())

def run_scheduler(app):
    schedule.every().day.at("08:00").do(send_morning_briefings, app)
    while True:
        schedule.run_pending()
        time.sleep(60)

def main():
    print("🌤️ DayMate is starting up...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    news_handler = ConversationHandler(
        entry_points=[CommandHandler("news", news_command)],
        states={
            WAITING_FOR_INTERESTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_interests)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    bill_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.PHOTO, handle_photo)],
        states={
            WAITING_FOR_PEOPLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_num_people)],
            WAITING_FOR_TIP: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_tip)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("briefing", briefing_command))
    app.add_handler(news_handler)
    app.add_handler(bill_handler)

    scheduler_thread = threading.Thread(target=run_scheduler, args=(app,), daemon=True)
    scheduler_thread.start()

    print("✅ DayMate is running! Open Telegram and message your bot.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()