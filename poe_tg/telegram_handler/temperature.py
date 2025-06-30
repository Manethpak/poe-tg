from telegram import Update
from telegram.ext import ContextTypes
from ..database import set_user_preference


async def set_temperature(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set the temperature for AI responses."""
    if not update.effective_user or not update.message:
        return
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
        await update.message.reply_text(
            "Please provide a valid number between 0.0 and 1.0."
        )
