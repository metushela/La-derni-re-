import json
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "7980302462:AAFS3EBrr1qaeWVwsY63W_fusboMlNKETE8"  # Remplace par ton token BotFather
FICHIER_QR = "base_qr.json"

# Charger la base de données
def charger_base():
    if os.path.exists(FICHIER_QR):
        with open(FICHIER_QR, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Sauvegarder la base de données
def sauvegarder_base(base):
    with open(FICHIER_QR, "w", encoding="utf-8") as f:
        json.dump(base, f, ensure_ascii=False, indent=2)

base_qr = charger_base()
en_attente = {}

# Clavier personnalisé
clavier = ReplyKeyboardMarkup(
    [
        [KeyboardButton("📄 Lister les questions")],
        [KeyboardButton("➕ Apprendre une question")],
        [KeyboardButton("❌ Oublier une question")]
    ],
    resize_keyboard=True
)

# Commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salut ! Utilise les boutons ci-dessous ou pose-moi une question.",
        reply_markup=clavier
    )

# Commande /forget
async def forget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Utilisation : /forget question à effacer")
        return

    question = " ".join(context.args).lower().strip()
    if question in base_qr:
        del base_qr[question]
        sauvegarder_base(base_qr)
        await update.message.reply_text(f"La question « {question} » a été oubliée.")
    else:
        await update.message.reply_text("Je ne connais pas cette question.")

# Commande /list
async def lister(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not base_qr:
        await update.message.reply_text("Je n’ai encore appris aucune question.")
    else:
        questions = "\n".join(f"- {q}" for q in base_qr.keys())
        await update.message.reply_text(f"Voici les questions que je connais :\n{questions}")

# Réponse aux messages
async def repondre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    texte = update.message.text.strip().lower()

    # Réactions aux boutons
    if texte == "📄 lister les questions":
        if not base_qr:
            await update.message.reply_text("Je ne connais encore aucune question.")
        else:
            questions = "\n".join(f"- {q}" for q in base_qr.keys())
            await update.message.reply_text(f"Voici ce que je connais :\n{questions}")
        return

    if texte == "➕ apprendre une question":
        await update.message.reply_text("Pose-moi directement ta question, puis je te demanderai sa réponse.")
        return

    if texte == "❌ oublier une question":
        await update.message.reply_text("Utilise la commande : /forget ta question exacte.")
        return

    # Si en mode apprentissage
    if user_id in en_attente:
        question = en_attente.pop(user_id)
        base_qr[question] = texte
        sauvegarder_base(base_qr)
        await update.message.reply_text("Merci ! J’ai bien retenu ça.")
        return

    # Si la question est connue
    if texte in base_qr:
        await update.message.reply_text(base_qr[texte])
    elif texte.endswith("?"):
        await update.message.reply_text("Je ne connais pas encore cette réponse. Peux-tu me dire quoi répondre ?")
        en_attente[user_id] = texte
    else:
        await update.message.reply_text("Pose-moi une question ou utilise les boutons ci-dessous.")

# Lancer le bot
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("forget", forget))
app.add_handler(CommandHandler("list", lister))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, repondre))
app.run_polling()