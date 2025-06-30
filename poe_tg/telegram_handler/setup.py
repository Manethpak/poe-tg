from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)
from . import (
    start,
    help_command,
    settings,
    select_bot,
    button_callback,
    handle_message,
    clear_history,
    set_system_prompt,
    set_temperature,
)


def setup_handlers(application: Application) -> None:
    """Set up all the handlers for the Telegram bot."""
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("select_bot", select_bot))
    application.add_handler(CommandHandler("settings", settings))
    application.add_handler(CommandHandler("set_system_prompt", set_system_prompt))
    application.add_handler(CommandHandler("set_temperature", set_temperature))
    application.add_handler(CommandHandler("clear_history", clear_history))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
