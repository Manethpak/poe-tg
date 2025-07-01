import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from poe_tg import config
from poe_tg.poe_client import get_poe_response
from poe_tg.utils import split_message
from poe_tg.db.database import get_user_preference


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle user messages and forward them to Poe."""
    if not update.effective_user or not update.message or not update.message.text:
        return
    username = update.effective_user.username
    if config.AUTHORIZATION:
        if username not in config.AUTHORIZED_USERS:
            await update.message.reply_text("You are not authorized to use this bot.")
            return

    user_id = update.effective_user.id
    user_message = update.message.text

    # Get the user's preferred bot from the database
    preference = get_user_preference(user_id)

    # Send a "typing" action
    if update.effective_message:
        await context.bot.send_chat_action(
            chat_id=update.effective_message.chat_id, action="typing"
        )

    # Get response from Poe with conversation history
    response = await get_poe_response(user_message, preference["bot_name"], user_id)

    # Split the response if it's too long
    message_chunks = split_message(response)

    # Send each chunk as a separate message
    for chunk in message_chunks:
        await update.message.reply_text(chunk)
        # Small delay between messages to maintain order
        if len(message_chunks) > 1:
            await asyncio.sleep(0.5)
