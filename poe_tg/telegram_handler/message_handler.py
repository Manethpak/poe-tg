import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from poe_tg import config
from poe_tg.poe_client import get_poe_response
from poe_tg.utils import split_message
from poe_tg.telegram_handler.select_bot import handle_custom_bot_name


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle user messages and forward them to Poe."""
    if not update.effective_user or not update.message:
        return

    if config.AUTHORIZATION:
        if update.effective_user.username not in config.AUTHORIZED_USERS:
            await update.message.reply_text("You are not authorized to use this bot.")
            return

    user_id = update.effective_user.id

    # Check if user is expecting to input a custom bot name
    if (
        context.user_data
        and user_id in context.user_data
        and context.user_data[user_id].get("expecting_custom_bot")
    ):
        await handle_custom_bot_name(update, context)
        return

    # Send a "typing" action
    if update.effective_message:
        await context.bot.send_chat_action(
            chat_id=update.effective_message.chat_id, action="typing"
        )

    response = await get_poe_response(update, context)

    # Split the response if it's too long
    message_chunks = split_message(response)

    # Send each chunk as a separate message
    for chunk in message_chunks:
        await update.message.reply_text(chunk)
        # Small delay between messages to maintain order
        if len(message_chunks) > 1:
            await asyncio.sleep(0.5)
