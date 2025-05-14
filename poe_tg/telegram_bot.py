import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

from . import config
from .poe_client import get_poe_response
from .utils import split_message
from .database import clear_conversation_history, get_user_preference, set_user_preference

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user_id = update.effective_user.id
    set_user_preference(user_id, bot_name=config.DEFAULT_BOT, temperature=0.7, system_prompt="")
    
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
        "/settings - Show your current settings\n"
        "/set_system_prompt - Set a custom system prompt\n"
        "/set_temperature - Set the temperature for AI responses\n"
        "/clear_history - Clear your conversation history"
    )

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show all user settings."""
    user_id = update.effective_user.id
    user_settings = get_user_preference(user_id)
    
    await update.message.reply_text(
        f"Your current settings:\n\n"
        f"AI Model: {user_settings['bot_name']}\n"
        f"Temperature: {user_settings['temperature']}\n"
        f"System Prompt: {user_settings['system_prompt'] or 'Not set'}"
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
        set_user_preference(user_id, bot_name=selected_bot)
        
        await query.edit_message_text(f"Selected AI model: {selected_bot}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle user messages and forward them to Poe."""
    username = update.effective_user.username
    if config.AUTHORIZATION:
        if username not in config.AUTHORIZED_USERS:
            await update.message.reply_text("You are not authorized to use this bot.")
            return

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

async def set_system_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set a custom system prompt for the AI."""
    user_id = update.effective_user.id
    
    # Check if there's a prompt in the message
    if not context.args:
        await update.message.reply_text(
            "Please provide a system prompt after the command.\n"
            "Example: /set_system_prompt You are a helpful assistant.\n\n"
            "To clear the system prompt, use: /set_system_prompt clear"
        )
        return
    
    # Join all arguments to form the prompt
    prompt = " ".join(context.args)
    
    # Check if user wants to clear the prompt
    if prompt.lower() == "clear":
        prompt = ""
        success_message = "System prompt cleared."
    else:
        success_message = f"System prompt set to: {prompt}"
    
    # Update the user's system prompt
    set_user_preference(user_id, system_prompt=prompt)
    
    await update.message.reply_text(success_message)

async def set_temperature(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set the temperature for AI responses."""
    user_id = update.effective_user.id
    
    # Check if there's a temperature value in the message
    if not context.args:
        await update.message.reply_text(
            "Please provide a temperature value between 0.0 and 1.0 after the command.\n"
            "Example: /set_temperature 0.7\n\n"
            "Lower values (e.g., 0.2) make responses more focused and deterministic.\n"
            "Higher values (e.g., 0.8) make responses more creative and varied."
        )
        return
    
    try:
        temperature = float(context.args[0])
        
        # Validate temperature range
        if temperature < 0.0 or temperature > 1.0:
            await update.message.reply_text("Temperature must be between 0.0 and 1.0.")
            return
        
        # Update the user's temperature setting
        set_user_preference(user_id, temperature=temperature)
        
        await update.message.reply_text(f"Temperature set to: {temperature}")
    except ValueError:
        await update.message.reply_text("Please provide a valid number between 0.0 and 1.0.")

def setup_handlers(application: Application):
    """Set up all the handlers for the Telegram bot."""
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("select_bot", select_bot))
    application.add_handler(CommandHandler("settings", settings))
    application.add_handler(CommandHandler("set_system_prompt", set_system_prompt))
    application.add_handler(CommandHandler("set_temperature", set_temperature))
    application.add_handler(CommandHandler("clear_history", clear_history)) 
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))