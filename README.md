# Poe Telegram Bot

A Telegram bot that connects to Poe AI models, allowing you to chat with various AI assistants directly from Telegram.

## Features

- [x] Chat with multiple AI models from Poe (Claude, GPT-4, etc.)
- [x] Switch between different AI models with a simple command
- [x] Persistent conversation history for contextual responses
- [x] Automatic message splitting for long responses
- [x] Simple authorization for restricted access
- [x] Custom system prompt for conversation.
- [x] Handling file uploads and downloads from Poe
- [ ] Format markdown response to Telegram.

## Available Commands

- /start - Start the bot
- /help - Show this help message
- /select_bot - Choose which AI model to use
- /settings - Show your current settings
- /set_system_prompt - Set a custom system prompt
- /set_temperature - Set the temperature for AI responses
- /clear_history - Clear your conversation history

## Supported AI Models

Any model supported by Poe. Update your desired bot models in the `DEFAULT_BOT` and `AVAILABLE_BOTS` list in [`config.py`](https://github.com/Manethpak/poe-tg/blob/main/poe_tg/config.py)

## Installation

### Prerequisites

- Python 3.10 or higher
- Poetry (for dependency management)
- Telegram Bot Token
- Poe API Key

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/manethpak/poe-tg.git
   cd poe-tg
   ```

2. Install dependencies using Poetry:

   ```bash
   poetry install
   ```

3. Create a `.env` file in the project root with your API keys:

   ```properties
   TELEGRAM_TOKEN=your_telegram_bot_token
   POE_API_KEY=your_poe_api_key
   WEBHOOK_URL=https://URL_ADDRESS # Running app in webhook mode
   # Optional
   AUTHORIZATION=true # Default to false
   AUTHORIZED_USERS=user1,user2
   ```

   Go to https://poe.com/api_key to get your Poe's API key.

4. Run the bot:

   ```bash
   # Production mode (Webhook mode)
   poetry run start

   # Dev mode (Polling mode)
   poetry run dev
   ```

## Project Structure

- `poe_tg/` - Main package directory
  - `__init__.py` - Package initialization
  - `main.py` - Entry point for the application
  - `config.py` - Configuration settings and environment variables
  - `telegram_bot.py` - Telegram bot handlers and setup
  - `poe_client.py` - Client for interacting with Poe API
  - `database.py` - SQLite database operations
  - `utils.py` - Utility functions (message splitting, etc.)

## Database

The application uses PostgreSQL for persistent storage with SQLAlchemy ORM and Alembic for migrations:

### Database Setup

1. Set the `DATABASE_URL` environment variable in your `.env` file:
   ```properties
   DATABASE_URL=postgresql://username:password@localhost/database_name
   ```

2. Initialize the database and run migrations:
   ```bash
   poetry run alembic upgrade head
   ```

### Database Management

For detailed database management commands and migration workflows, see [Database Documentation](poe_tg/db/database.md).

The database schema is automatically created and managed through Alembic migrations, ensuring version control for your database structure.

## License

MIT

## Author

Maneth Pak <manethpak00@gmail.com>
