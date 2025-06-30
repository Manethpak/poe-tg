from .start import start
from .help import help_command
from .settings import settings
from .select_bot import select_bot, button_callback
from .message_handler import handle_message
from .clear_history import clear_history
from .system_prompt import set_system_prompt
from .temperature import set_temperature
from .setup import setup_handlers

__all__ = [
    "start",
    "help_command",
    "settings",
    "select_bot",
    "button_callback",
    "handle_message",
    "clear_history",
    "set_system_prompt",
    "set_temperature",
    "setup_handlers",
]

"""
poe_tg/telegram_handler/
├── __init__.py          # Exports all handlers and setup function
├── setup.py             # Main setup function for registering handlers
├── start.py             # /start command handler
├── help.py              # /help command handler  
├── settings.py          # /settings command handler
├── select_bot.py        # /select_bot command and button callback
├── message_handler.py   # Main message processing handler
├── clear_history.py     # /clear_history command handler
├── system_prompt.py     # /set_system_prompt command handler
└── temperature.py       # /set_temperature command handler
"""
