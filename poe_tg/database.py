# TODO: adapter for cloud database

import sqlite3
from pathlib import Path
from . import config
from datetime import datetime
from typing import TypedDict
from typing_extensions import Unpack

# Database file path
DB_PATH = Path(__file__).parent.parent / "user_data.db"


def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create user_preferences table
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS user_preferences (
        user_id INTEGER PRIMARY KEY,
        bot_name TEXT NOT NULL,
        system_prompt TEXT DEFAULT '',
        temperature REAL DEFAULT 0.7
    )
    """
    )

    # Create conversation_history table
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS conversation_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        timestamp TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        bot_name TEXT NOT NULL
    )
    """
    )

    conn.commit()
    conn.close()

    config.logger.info(f"Database initialized at {DB_PATH}")


def get_user_preference(user_id):
    """Get a user preference settings from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user_preferences WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    conn.close()

    # Return default preferences if no result found
    if not result:
        return {"bot_name": config.DEFAULT_BOT, "system_prompt": "", "temperature": 0.7}

    # Only access result tuple if it exists
    return {"bot_name": result[1], "system_prompt": result[2], "temperature": result[3]}


class UserSettingParams(TypedDict, total=False):
    bot_name: str
    system_prompt: str | None
    temperature: float | None


def set_user_preference(user_id, **kwargs: Unpack[UserSettingParams]):
    """
    Set a user's preference settings in the database.

    Args:
        user_id (int): The user's ID
        **kwargs: Keyword arguments for preference settings
        - bot_name (str)
        - system_prompt (str)
        - temperature (float)
    """
    if not kwargs:
        return  # No preferences to update

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # First, check if the user already has preferences
    cursor.execute("SELECT * FROM user_preferences WHERE user_id = ?", (user_id,))
    existing = cursor.fetchone()

    if existing:
        # Update only the provided fields
        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        query = f"UPDATE user_preferences SET {set_clause} WHERE user_id = ?"
        params = list(kwargs.values()) + [user_id]
        cursor.execute(query, params)
    else:
        # For new users, ensure we have default values for missing fields
        defaults = {
            "bot_name": config.DEFAULT_BOT,
            "system_prompt": "",
            "temperature": 0.7,
        }

        # Override defaults with provided values
        preferences = {**defaults, **kwargs}

        # Insert new record with all fields
        fields = ", ".join(preferences.keys())
        placeholders = ", ".join(["?"] * len(preferences))
        query = f"INSERT INTO user_preferences (user_id, {fields}) VALUES (?, {placeholders})"
        params = [user_id] + list(preferences.values())
        cursor.execute(query, params)

    conn.commit()
    conn.close()


def add_message_to_history(user_id, role, content, bot_name):
    """Add a message to the conversation history."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    timestamp = datetime.now().isoformat()

    cursor.execute(
        """
    INSERT INTO conversation_history (user_id, timestamp, role, content, bot_name)
    VALUES (?, ?, ?, ?, ?)
    """,
        (user_id, timestamp, role, content, bot_name),
    )

    conn.commit()
    conn.close()


def get_conversation_history(user_id, limit=10):
    """Get the recent conversation history for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
    SELECT role, content FROM conversation_history
    WHERE user_id = ?
    ORDER BY timestamp DESC
    LIMIT ?
    """,
        (user_id, limit),
    )

    # Fetch results and reverse to get chronological order
    results = cursor.fetchall()
    results.reverse()

    conn.close()

    # Convert to list of message objects
    messages = []
    for role, content in results:
        messages.append({"role": role, "content": content})

    return messages


def clear_conversation_history(user_id):
    """Clear the conversation history for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM conversation_history WHERE user_id = ?", (user_id,))

    conn.commit()
    conn.close()
