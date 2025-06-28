import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Basic config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("7640201865:AAFE4d1BiCCwcqLllqXg3FncCoYoZ3Os39I")
DEVELOPER_CHAT_ID = "6718568837"
DEVELOPER_USERNAME = "@Dark_code_yeu"

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Contact Developer", callback_data="contact_dev")],
        [InlineKeyboardButton("Report Glitch", callback_data="report_glitch")],
        [InlineKeyboardButton("Report Spam Account", callback_data="report_spam")],
        [InlineKeyboardButton("📢 Give Recommendation", callback_data="give_recommendation")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 Welcome to WeShare Support!\nWhat would you like to do?",
        reply_markup=reply_markup
    )

# Handle button clicks
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "contact_dev":
        await query.edit_message_text(f"📨 Contact the developer: https://t.me/{DEVELOPER_USERNAME}")
    elif query.data == "report_glitch":
        context.user_data['report'] = {'type': 'glitch', 'stage': 'awaiting_input'}
        await query.edit_message_text("🛠 Please send a **screenshot**, **voice**, or **message** describing the glitch.")
    elif query.data == "report_spam":
        context.user_data['report'] = {'type': 'spam', 'stage': 'awaiting_username'}
        await query.edit_message_text("🔍 Please send the spam username (@format).")
    elif query.data == "give_recommendation":
        context.user_data['report'] = {'type': 'recommendation', 'stage': 'awaiting_input'}
        await query.edit_message_text("💡 Please send your recommendation or voice message.")

# Handle user input (photo, voice, text)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if 'report' not in context.user_data:
        return

    report = context.user_data['report']
    user = update.effective_user
    report_type = report['type']

    if report_type in ['glitch', 'recommendation']:
        message_parts = [f"📩 New {report_type.upper()} from {user.mention_html()}"]

        # Handle text
        if update.message.text:
            message_parts.append(f"📝 Message:\n{update.message.text}")
        
        # Send base message
        await context.bot.send_message(
            chat_id=DEVELOPER_CHAT_ID,
            text="\n\n".join(message_parts),
            parse_mode="HTML"
        )

        # Handle voice
        if update.message.voice:
            file = await update.message.voice.get_file()
            await file.download_to_drive("voice_note.ogg")
            await context.bot.send_voice(
                chat_id=DEVELOPER_CHAT_ID,
                voice=open("voice_note.ogg", "rb")
            )

        # Handle photo
        if update.message.photo:
            photo_file = await update.message.photo[-1].get_file()
            await photo_file.download_to_drive("glitch.jpg")
            await context.bot.send_photo(
                chat_id=DEVELOPER_CHAT_ID,
                photo=open("glitch.jpg", "rb")
            )

        await update.message.reply_text("✅ Thank you! Your feedback has been sent.")
        context.user_data.clear()

    elif report_type == 'spam' and update.message.text.startswith("@"):
        await context.bot.send_message(
            chat_id=DEVELOPER_CHAT_ID,
            text=f"⚠️ Spam Report from {user.mention_html()}\nUsername: {update.message.text}",
            parse_mode='HTML'
        )
        await update.message.reply_text("✅ Thanks! The spam account has been reported.")
        context.user_data.clear()

# Main bot runner
def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.VOICE, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
