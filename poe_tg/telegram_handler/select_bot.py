from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from poe_tg import config
from poe_tg.db.database import set_user_preference


async def select_bot(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    """Let the user select which bot to use."""
    if not update.message:
        return
    keyboard = []
    for bot in config.AVAILABLE_BOTS:
        keyboard.append([InlineKeyboardButton(bot, callback_data=f"bot_{bot}")])

    # Add custom bot option
    keyboard.append(
        [InlineKeyboardButton("📝 Write custom bot name", callback_data="custom_bot")]
    )

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Please select an AI model or write your own:", reply_markup=reply_markup
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

    elif query.data == "custom_bot":
        # Store user state to expect custom bot name
        user_id = update.effective_user.id
        if context.user_data is None:
            context.user_data = {}
        context.user_data[user_id] = {"expecting_custom_bot": True}

        await query.edit_message_text(
            "Please type the name of the bot you want to use:\n\n"
            "Examples:\n"
            "- Claude-3.5-Sonnet\n"
            "- GPT-4o\n"
            "- Claude-3.7-Sonnet\n"
            "- Any other bot name available on Poe"
        )


async def handle_custom_bot_name(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle custom bot name input from user."""
    if not update.message or not update.effective_user:
        return

    user_id = update.effective_user.id

    # Check if user is expecting to input a custom bot name
    if (
        context.user_data
        and user_id in context.user_data
        and context.user_data[user_id].get("expecting_custom_bot")
    ):
        custom_bot_name = update.message.text.strip() if update.message.text else ""

        if custom_bot_name:
            # Save the custom bot name
            set_user_preference(
                user_id, bot_name=custom_bot_name, system_prompt="", temperature=0.7
            )

            # Clear the expecting state
            if context.user_data and user_id in context.user_data:
                del context.user_data[user_id]["expecting_custom_bot"]

            await update.message.reply_text(
                f"✅ Custom AI model set to: {custom_bot_name}\n\n"
                "You can now start chatting with this model!"
            )
        else:
            await update.message.reply_text(
                "❌ Please provide a valid bot name. Try again or use /select_bot to choose from the list."
            )
