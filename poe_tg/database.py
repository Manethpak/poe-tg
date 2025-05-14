import sqlite3
from pathlib import Path
from . import config
from datetime import datetime

# Database file path
DB_PATH = Path(__file__).parent.parent / "user_data.db"

def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create user_preferences table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_preferences (
        user_id INTEGER PRIMARY KEY,
        bot_name TEXT NOT NULL
    )
    ''')
    
    # Create conversation_history table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS conversation_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        timestamp TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        bot_name TEXT NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()
    
    config.logger.info(f"Database initialized at {DB_PATH}")

def get_user_preference(user_id):
    """Get a user's preferred bot from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT bot_name FROM user_preferences WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return result[0]
    return config.DEFAULT_BOT

def set_user_preference(user_id, bot_name):
    """Set a user's preferred bot in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT OR REPLACE INTO user_preferences (user_id, bot_name)
    VALUES (?, ?)
    ''', (user_id, bot_name))
    
    conn.commit()
    conn.close()

def add_message_to_history(user_id, role, content, bot_name):
    """Add a message to the conversation history."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    timestamp = datetime.now().isoformat()
    
    cursor.execute('''
    INSERT INTO conversation_history (user_id, timestamp, role, content, bot_name)
    VALUES (?, ?, ?, ?, ?)
    ''', (user_id, timestamp, role, content, bot_name))
    
    conn.commit()
    conn.close()

def get_conversation_history(user_id, limit=10):
    """Get the recent conversation history for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT role, content FROM conversation_history
    WHERE user_id = ?
    ORDER BY timestamp DESC
    LIMIT ?
    ''', (user_id, limit))
    
    # Fetch results and reverse to get chronological order
    results = cursor.fetchall()
    results.reverse()
    
    conn.close()
    
    # Convert to list of message objects
    messages = []
    for role, content in results:
        messages.append({"role": role, "content": content})
    
    return messages

# Add this function to database.py
def clear_conversation_history(user_id):
    """Clear the conversation history for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM conversation_history WHERE user_id = ?", (user_id,))
    
    conn.commit()
    conn.close()