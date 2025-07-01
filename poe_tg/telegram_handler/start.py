from telegram import Update
from telegram.ext import ContextTypes
from poe_tg import config
from poe_tg.db.database import set_user_preference


async def start(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    if not update.effective_user or not update.message:
        return

    user_id = update.effective_user.id
    set_user_preference(
        user_id,
        bot_name=config.DEFAULT_BOT,
        temperature=0.7,
        system_prompt="""
    You are a friendly, conversational assistant who  speaks naturally like a real person. 
    Keep your responses casual, warm, and engaging.
    Use a relaxed tone with occasional humor when appropriate. 
    Don't be overly formal or robotic - it's okay to use contractions, simple language, and shorter sentences.
    Ask follow-up questions to show interest in the conversation. Avoid long explanations unless specifically requested.
    Your goal is to make the conversation feel like chatting with a helpful friend rather than interacting with a machine.
    """,
    )

    username = update.effective_user.username

    if config.AUTHORIZATION:
        if username not in config.AUTHORIZED_USERS:
            await update.message.reply_text("You are not authorized to use this bot.")
            return

    await update.message.reply_text(
        f"Hello! I'm a bot that connects to Poe AI models. "
        f"Currently using: {config.DEFAULT_BOT}\n\n"
        f"You can change the AI model with /select_bot"
    )
