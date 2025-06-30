from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from .. import config
from ..database import set_user_preference


async def select_bot(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    """Let the user select which bot to use."""
    if not update.message:
        return
    keyboard = []
    for bot in config.AVAILABLE_BOTS:
        keyboard.append([InlineKeyboardButton(bot, callback_data=f"bot_{bot}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Please select an AI model:", reply_markup=reply_markup
    )


async def button_callback(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks for bot selection."""
    if not update.callback_query or not update.effective_user:
        return
    query = update.callback_query
    await query.answer()

    if query.data and query.data.startswith("bot_"):
        selected_bot = query.data[4:]  # Remove "bot_" prefix
        user_id = update.effective_user.id
        set_user_preference(
            user_id, bot_name=selected_bot, system_prompt="", temperature=0.7
        )

        await query.edit_message_text(f"Selected AI model: {selected_bot}")
