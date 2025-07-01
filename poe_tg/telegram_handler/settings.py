from telegram import Update
from telegram.ext import ContextTypes
from poe_tg.db.database import get_user_preference


async def settings(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show all user settings."""
    if not update.effective_user or not update.message:
        return
    user_id = update.effective_user.id
    user_settings = get_user_preference(user_id)

    await update.message.reply_text(
        f"Your current settings:\n\n"
        f"AI Model: {user_settings['bot_name']}\n"
        f"Temperature: {user_settings['temperature']}\n"
        f"System Prompt: {user_settings['system_prompt'] or 'Not set'}"
    )
