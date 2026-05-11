import os
import json
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 5242660904

AOKBET_CHANNEL_ID = -1002742597937
AOKBET_LINK = "https://t.me/+4tUnDFWg4gVlM2Q0"

CLUB_PRIVE_LINK = "https://t.me/+eP4JoJiX8qU3ZmZk"

WELCOME_IMAGE = "welcome.jpg"
TRACKING_FILE = "visitors.json"
CLICK_COOLDOWN_SECONDS = 20


def load_tracking():
    try:
        with open(TRACKING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_tracking(data):
    with open(TRACKING_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def is_today(iso_time):
    try:
        return datetime.fromisoformat(iso_time).date() == datetime.now().date()
    except Exception:
        return False


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


def set_alerts_enabled(user):
    data = load_tracking()
    user_id = str(user.id)

    if user_id not in data:
        data[user_id] = {
            "username": user.username,
            "first_name": user.first_name,
            "first_seen": datetime.now().isoformat(),
            "actions": []
        }

    data[user_id]["alerts_enabled"] = True
    data[user_id]["alerts_enabled_at"] = datetime.now().isoformat()
    data[user_id]["last_seen"] = datetime.now().isoformat()
    data[user_id]["last_action"] = "alerts_enabled"
    data[user_id]["actions"].append({
        "action": "alerts_enabled",
        "time": datetime.now().isoformat()
    })

    save_tracking(data)


async def activate_alerts_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    set_alerts_enabled(query.from_user)

    await query.answer("Alertes privées activées 🔔", show_alert=True)

    await query.message.reply_text(
        "✅ Alertes privées activées 🔔🔥\n\n"
        "Tu fais maintenant partie des membres du bot AokBet.\n\n"
        "Tu pourras recevoir en privé :\n"
        "🔥 1 MOIS VIP OFFERT via tirage au sort\n"
        "💸 20€ OFFERTS IMMÉDIATEMENT\n"
        "⚽ Combinés exclusifs\n"
        "🎾 Leaks tennis rentables\n"
        "🚨 Grosses alertes live\n\n"
        "Reste connecté, certains bets ne seront envoyés qu’ici 😈"
    )


async def alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    set_alerts_enabled(update.effective_user)

    await update.message.reply_text(
        "✅ Alertes privées activées 🔔🔥\n\n"
        "Tu fais maintenant partie des membres du bot AokBet.\n\n"
        "Tu pourras recevoir en privé :\n"
        "🔥 1 MOIS VIP OFFERT via tirage au sort\n"
        "💸 20€ OFFERTS IMMÉDIATEMENT\n"
        "⚽ Combinés exclusifs\n"
        "🎾 Leaks tennis rentables\n"
        "🚨 Grosses alertes live\n\n"
        "Reste connecté, certains bets ne seront envoyés qu’ici 😈"
    )


async def alertpost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Accès refusé.")
        return

    text = (
        "🚨 BOT PRIVÉ AOKBET 🚨\n\n"
        "Les membres du bot reçoivent :\n\n"
        "🔥 1 MOIS VIP OFFERT\n"
        "💸 20€ OFFERTS IMMÉDIATEMENT\n"
        "⚽ Combinés exclusifs\n"
        "🎾 Leaks tennis rentables\n\n"
        "⚠️ Certains gros bets / live seront envoyés UNIQUEMENT sur le bot privé.\n\n"
        "👇 Active ton accès maintenant :"
    )

    keyboard = [
        [InlineKeyboardButton("🔔 Activer les alertes privées", callback_data="activate_alerts")]
    ]

    await context.bot.send_message(
        chat_id=AOKBET_CHANNEL_ID,
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await update.message.reply_text("✅ Post envoyé dans AokBet avec bouton.")


async def reminder_job(context: ContextTypes.DEFAULT_TYPE):
    job_data = context.job.data
    user_id = job_data["user_id"]

    data = load_tracking()
    user = data.get(str(user_id), {})

    if user.get("last_action") != "club_prive_unlocked":
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "👀 Tu n’as pas encore débloqué ton accès au Club Privé.\n\n"
                "Rejoins AokBet puis clique sur « ✅ J’ai rejoint AokBet » pour recevoir le lien 🔥"
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔥 Rejoindre AokBet", url=AOKBET_LINK)],
                [InlineKeyboardButton("✅ J’ai rejoint AokBet", callback_data="check_join")]
            ])
        )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update.effective_user, "start")

    context.job_queue.run_once(
        reminder_job,
        when=600,
        data={"user_id": update.effective_user.id},
        name=f"reminder_{update.effective_user.id}"
    )

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
        "Avant de débloquer le Club Privé, rejoins d’abord le canal AokBet ⚽🎾\n\n"
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
    data = load_tracking()
    user_data = data.get(str(user_id), {})

    last_click = user_data.get("last_check_click")
    if last_click:
        last_click_dt = datetime.fromisoformat(last_click)
        if datetime.now() - last_click_dt < timedelta(seconds=CLICK_COOLDOWN_SECONDS):
            await query.answer("Patiente quelques secondes avant de recliquer ⏳", show_alert=True)
            return

    user_data["last_check_click"] = datetime.now().isoformat()
    data[str(user_id)] = user_data
    save_tracking(data)

    track_user(query.from_user, "clicked_check_join")

    try:
        member = await context.bot.get_chat_member(AOKBET_CHANNEL_ID, user_id)

        if member.status in ["member", "administrator", "creator"]:
            track_user(query.from_user, "club_prive_unlocked")

            await query.message.reply_text(
                "✅ Accès validé 😈🔥\n\n"
                "Bienvenue dans le Club Privé FR 🔥\n"
                "Les exclus t’attendent ici 👇\n\n"
                f"{CLUB_PRIVE_LINK}\n\n"
                "⚽🎾 Et pour les vrais picks rentables :\n"
                "le VIP AokBet est seulement à 10€/mois avec plusieurs pronos par jour 💰"
            )
        else:
            track_user(query.from_user, "failed_not_in_aokbet")
            await query.answer("Rejoins d’abord AokBet pour débloquer le Club Privé 🔒", show_alert=True)

    except Exception as e:
        track_user(query.from_user, "verification_error")
        await query.answer(
            "Erreur de vérification. Vérifie que le bot est bien admin dans AokBet.",
            show_alert=True
        )
        print(e)


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Accès refusé.")
        return

    data = load_tracking()
    today_users = set()
    checked = 0
    unlocked = 0
    failed = 0
    alerts_today = 0
    alerts_total = 0

    for user_id, user_data in data.items():
        if user_data.get("alerts_enabled"):
            alerts_total += 1

        actions_today = [
            a for a in user_data.get("actions", [])
            if is_today(a.get("time"))
        ]

        if actions_today:
            today_users.add(user_id)

        if any(a["action"] == "clicked_check_join" for a in actions_today):
            checked += 1

        if any(a["action"] == "club_prive_unlocked" for a in actions_today):
            unlocked += 1

        if any(a["action"] == "failed_not_in_aokbet" for a in actions_today):
            failed += 1

        if any(a["action"] == "alerts_enabled" for a in actions_today):
            alerts_today += 1

    await update.message.reply_text(
        "📊 Stats du jour\n\n"
        f"👀 Visiteurs aujourd’hui : {len(today_users)}\n"
        f"✅ Clics vérification : {checked}\n"
        f"🔓 Accès Club débloqués : {unlocked}\n"
        f"❌ Refusés pas encore AokBet : {failed}\n\n"
        f"🔔 Alertes activées aujourd’hui : {alerts_today}\n"
        f"📩 Total membres alertes : {alerts_total}"
    )


app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("alerts", alerts))
app.add_handler(CommandHandler("alertpost", alertpost))
app.add_handler(CommandHandler("stats", stats))

app.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))
app.add_handler(CallbackQueryHandler(activate_alerts_button, pattern="activate_alerts"))

print("Bot lancé...")
app.run_polling()
