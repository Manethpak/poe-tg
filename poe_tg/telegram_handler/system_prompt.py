from telegram import Update
from telegram.ext import ContextTypes
from ..database import set_user_preference


async def set_system_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set a custom system prompt for the AI."""
    if not update.effective_user or not update.message:
        return
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
