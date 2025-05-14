from telegram.ext import ApplicationBuilder
from . import config
from .telegram_bot import setup_handlers
from .database import init_db

def main():
    """Start the bot."""
    # Initialize the database
    init_db()
    
    if not config.TELEGRAM_TOKEN:
        config.logger.error("No Telegram token provided. Set the TELEGRAM_TOKEN in the .env file.")
        return
        
    # Create the Application
    application = ApplicationBuilder().token(config.TELEGRAM_TOKEN).build()

    # Add handlers
    setup_handlers(application)

    # Start the Bot
    application.run_polling()

if __name__ == "__main__":
    main()