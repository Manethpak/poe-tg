from telegram import Update
from telegram.ext import ContextTypes


async def help_command(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    if not update.message:
        return
    await update.message.reply_text(
        "Just send me a message and I'll forward it to the selected AI model.\n\n"
        "Available commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/select_bot - Choose which AI model to use (or write your own)\n"
        "/settings - Show your current settings\n"
        "/set_system_prompt - Set a custom system prompt\n"
        "/set_temperature - Set the temperature for AI responses\n"
        "/clear_history - Clear your conversation history"
    )
