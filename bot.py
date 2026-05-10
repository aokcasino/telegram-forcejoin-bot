import os
import json
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

AOKBET_CHANNEL_ID = -1002742597937
AOKBET_LINK = "https://t.me/+4tUnDFWg4gVlM2Q0"

CLUB_PRIVE_LINK = "https://t.me/+eP4JoJiX8qU3ZmZk"

WELCOME_IMAGE = "welcome.jpg"
TRACKING_FILE = "visitors.json"


def load_tracking():
    try:
        with open(TRACKING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_tracking(data):
    with open(TRACKING_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def track_user(user, action):
    data = load_tracking()
    user_id = str(user.id)

    if user_id not in data:
        data[user_id] = {
            "username": user.username,
            "first_name": user.first_name,
            "first_seen": datetime.now().isoformat(),
            "actions": []
        }

    data[user_id]["last_action"] = action
    data[user_id]["last_seen"] = datetime.now().isoformat()
    data[user_id]["actions"].append({
        "action": action,
        "time": datetime.now().isoformat()
    })

    save_tracking(data)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update.effective_user, "start")

    keyboard = [
        [InlineKeyboardButton("🔥 Rejoindre AokBet", url=AOKBET_LINK)],
        [InlineKeyboardButton("✅ J’ai rejoint AokBet", callback_data="check_join")]
    ]

    caption = (
        "🔥 ACCÈS CLUB PRIVÉ FR 🔥\n\n"
        "Le contenu qui tourne partout sur Twitter est ici 😈👇\n\n"
        "📸 Exclus FR privés\n"
        "💎 Contenus réservés\n"
        "🔥 Daily drops & pépites privées\n"
        "🚨 Accès réservé aux membres validés\n\n"
        "Avant de débloquer le Club Privé, rejoins d’abord notre canal principal AokBet ⚽🎾\n\n"
        "📊 Pronostics gratuits chaque jour\n"
        "🎯 Analyses Football & Tennis\n"
        "💰 Résultats et grosses cotes\n\n"
        "👇 Rejoins AokBet puis clique sur « ✅ J’ai rejoint AokBet »"
    )

    try:
        with open(WELCOME_IMAGE, "rb") as photo:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=photo,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except FileNotFoundError:
        await update.message.reply_text(
            caption,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    track_user(query.from_user, "clicked_check_join")

    try:
        member = await context.bot.get_chat_member(AOKBET_CHANNEL_ID, user_id)

        if member.status in ["member", "administrator", "creator"]:
            track_user(query.from_user, "club_prive_unlocked")

            await query.message.reply_text(
                "✅ Accès validé 😈🔥\n\n"
                "Bienvenue dans le Club Privé FR 🔥\n"
                "Les exclus t’attendent ici 👇\n\n"
                f"{CLUB_PRIVE_LINK}"
            )
        else:
            track_user(query.from_user, "failed_not_in_aokbet")

            await query.answer(
                "Rejoins d’abord AokBet pour débloquer le Club Privé 🔒",
                show_alert=True
            )

    except Exception as e:
        track_user(query.from_user, "verification_error")

        await query.answer(
            "Erreur de vérification. Vérifie que le bot est bien admin dans AokBet.",
            show_alert=True
        )
        print(e)


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_tracking()

    total = len(data)
    checked = sum(
        1 for u in data.values()
        if any(a["action"] == "clicked_check_join" for a in u.get("actions", []))
    )
    unlocked = sum(
        1 for u in data.values()
        if any(a["action"] == "club_prive_unlocked" for a in u.get("actions", []))
    )
    failed = sum(
        1 for u in data.values()
        if any(a["action"] == "failed_not_in_aokbet" for a in u.get("actions", []))
    )

    await update.message.reply_text(
        "📊 Stats bot\n\n"
        f"👀 Visiteurs /start : {total}\n"
        f"✅ Clics vérification : {checked}\n"
        f"🔓 Accès Club débloqués : {unlocked}\n"
        f"❌ Refusés pas encore AokBet : {failed}"
    )


app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))

print("Bot lancé...")
app.run_polling()
