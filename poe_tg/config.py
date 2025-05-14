import logging
from dotenv import dotenv_values

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables ONLY from .env file
env_vars = dotenv_values()

# Bot configuration
DEFAULT_BOT = "Claude-3.7-Sonnet"
AVAILABLE_BOTS = ["Claude-3.7-Sonnet", "GPT-4o", "GPT-4.1", "Claude-3.5-Sonnet"]

# API keys
POE_API_KEY = env_vars.get("POE_API_KEY")
TELEGRAM_TOKEN = env_vars.get("TELEGRAM_TOKEN")

# Telegram message character limit
TELEGRAM_MESSAGE_LIMIT = 4096

# Validate environment variables
if not POE_API_KEY:
    logger.error("POE_API_KEY not found in .env file. Please add it to your .env file.")
    
if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_TOKEN not found in .env file. Please add it to your .env file.")