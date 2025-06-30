from telegram import Update
from telegram.ext import ContextTypes
from ..database import clear_conversation_history


async def clear_history(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear the conversation history."""
    if not update.effective_user or not update.message:
        return
    user_id = update.effective_user.id
    clear_conversation_history(user_id)

    await update.message.reply_text("Your conversation history has been cleared.")
