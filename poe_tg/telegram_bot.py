import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

from . import config
from .poe_client import get_poe_response
from .utils import split_message
from .database import clear_conversation_history, get_user_preference, set_user_preference

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user_id = update.effective_user.id
    set_user_preference(user_id, config.DEFAULT_BOT)
    
    await update.message.reply_text(
        f"Hello! I'm a bot that connects to Poe AI models. "
        f"Currently using: {config.DEFAULT_BOT}\n\n"
        f"You can change the AI model with /select_bot"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "Just send me a message and I'll forward it to the selected AI model.\n"
        "Available commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/select_bot - Choose which AI model to use\n"
        "/current_bot - Show the current AI model you're using\n"
        "/clear_history - Clear your conversation history"
    )

async def select_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Let the user select which bot to use."""
    keyboard = []
    for bot in config.AVAILABLE_BOTS:
        keyboard.append([InlineKeyboardButton(bot, callback_data=f"bot_{bot}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please select an AI model:", reply_markup=reply_markup)

async def current_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the current bot the user is using."""
    user_id = update.effective_user.id
    bot_name = get_user_preference(user_id)
    await update.message.reply_text(f"You are currently using: {bot_name}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks for bot selection."""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("bot_"):
        selected_bot = query.data[4:]  # Remove "bot_" prefix
        user_id = update.effective_user.id
        set_user_preference(user_id, selected_bot)
        
        await query.edit_message_text(f"Selected AI model: {selected_bot}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle user messages and forward them to Poe."""
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # Get the user's preferred bot from the database
    bot_name = get_user_preference(user_id)
    
    # Send a "typing" action
    await context.bot.send_chat_action(
        chat_id=update.effective_message.chat_id,
        action="typing"
    )
    
    # Get response from Poe with conversation history
    response = await get_poe_response(user_message, bot_name, user_id)
    
    # Split the response if it's too long
    message_chunks = split_message(response)
    
    # Send each chunk as a separate message
    for chunk in message_chunks:
        await update.message.reply_text(chunk)
        # Small delay between messages to maintain order
        if len(message_chunks) > 1:
            await asyncio.sleep(0.5)

# Add this handler to telegram_bot.py
async def clear_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear the conversation history."""
    user_id = update.effective_user.id
    clear_conversation_history(user_id)
    
    await update.message.reply_text("Your conversation history has been cleared.")

# Update the setup_handlers function
def setup_handlers(application):
    """Set up all the handlers for the Telegram bot."""
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("select_bot", select_bot))
    application.add_handler(CommandHandler("current_bot", current_bot))
    application.add_handler(CommandHandler("clear_history", clear_history)) 
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))