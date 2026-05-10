from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "8542071255:AAFt29MyIA2Lj8PxIVF4tyjGuQfnofuySr4"

AOKBET_CHANNEL_ID = -1002742597937
AOKBET_LINK = "https://t.me/+4tUnDFWg4gVlM2Q0"

CLUB_PRIVE_LINK = "https://t.me/+eP4JoJiX8qU3ZmZk"

WELCOME_IMAGE = "welcome.jpg"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔥 Rejoindre AokBet pour débloquer", url=AOKBET_LINK)],
        [InlineKeyboardButton("✅ J’ai rejoint", callback_data="check_join")]
    ]

    caption = (
        "🔥 CLUB PRIVÉ FR 🔞\n\n"
        "Tu veux accéder aux exclus, drops privés et contenus réservés ? 👀😈\n\n"
        "Pour débloquer l’accès au Club Privé, rejoins d’abord notre canal principal AokBet 👇\n\n"
        "🎾 Pronos offerts\n"
        "📊 Analyses sportives\n"
        "💸 Grosses cotes & résultats\n"
        "🎁 Accès VIP & contenus exclusifs\n\n"
        "⚠️ L’accès au Club Privé est réservé aux membres AokBet.\n\n"
        "Une fois AokBet rejoint, clique sur « ✅ J’ai rejoint » 🔥"
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

    try:
        member = await context.bot.get_chat_member(AOKBET_CHANNEL_ID, user_id)

        if member.status in ["member", "administrator", "creator"]:
            await query.message.reply_text(
                "✅ Accès validé 😈🔥\n\n"
                "Bienvenue dans le Club Privé FR 🔞\n"
                "Les exclus t’attendent ici 👇\n\n"
                f"{CLUB_PRIVE_LINK}"
            )
        else:
            await query.answer(
                "Rejoins d’abord AokBet pour débloquer le Club Privé 🔒",
                show_alert=True
            )

    except Exception as e:
        await query.answer(
            "Erreur de vérification. Vérifie que le bot est bien admin dans AokBet.",
            show_alert=True
        )
        print(e)

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))

print("Bot lancé...")
app.run_polling()