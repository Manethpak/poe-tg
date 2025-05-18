import logging
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file if it exists
load_dotenv()

# Bot configuration
DEFAULT_BOT = "Claude-3.7-Sonnet"
AVAILABLE_BOTS = ["Claude-3.7-Sonnet", "GPT-4o", "GPT-4.1", "Claude-3.5-Sonnet"]

# API keys - try .env first, then fall back to environment variables
POE_API_KEY = os.getenv("POE_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Telegram message character limit
TELEGRAM_MESSAGE_LIMIT = 4096

# Authorized users by Telegram usernames
AUTHORIZATION = os.getenv("AUTHORIZATION", "false").lower() == "true"
AUTHORIZED_USERS = os.getenv("AUTHORIZED_USERS", "").split(",")

# Validate environment variables
if AUTHORIZATION:
    logger.info("Authorization is enabled. Only authorized users can use the bot.")

if not POE_API_KEY:
    logger.error("POE_API_KEY not found in environment variables. Please set it in your environment or .env file.")
    
if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_TOKEN not found in environment variables. Please set it in your environment or .env file.")