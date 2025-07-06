import os
import json
from fastapi_poe.types import Attachment
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import List, Any, Generator
from datetime import datetime
from poe_tg import config
from .models import Base, UserPreference, ConversationHistory


def deserialize_attachments(attachments_data: Any) -> List[Attachment]:
    """Deserialize JSON data back to Attachment objects."""
    if not attachments_data:
        return []

    if not isinstance(attachments_data, list):
        return []

    attachments = []
    for attachment_dict in attachments_data:
        if isinstance(attachment_dict, dict):
            # Create Attachment object from dict
            attachment = Attachment(
                url=attachment_dict.get("file_url", ""),
                content_type=attachment_dict.get("content_type", ""),
                name=attachment_dict.get("name", ""),
            )
            attachments.append(attachment)
        elif hasattr(attachment_dict, "file_url"):
            # Already an Attachment object
            attachments.append(attachment_dict)

    return attachments


# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Create engine
engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Get database session for FastAPI dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Session:
    """Get database session for direct use."""
    return SessionLocal()


def init_db():
    """Initialize the database and create tables."""
    Base.metadata.create_all(bind=engine)
    config.logger.info("Database initialized with SQLAlchemy")


def get_user_preference(user_id: int):
    """Get user preference settings from the database."""
    db = get_db_session()
    try:
        preference = (
            db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
        )

        if not preference:
            # Create a new preference and save it to the database
            preference = UserPreference(
                user_id=user_id,
                bot_name=config.DEFAULT_BOT,
                system_prompt="",
                temperature=0.7,
            )
            db.add(preference)
            db.commit()
            # Refresh the object to get the actual values
            db.refresh(preference)

        return preference
    finally:
        db.close()


def set_user_preference(user_id: int, **kwargs):
    """Set user preference settings in the database."""
    if not kwargs:
        return

    db = get_db_session()
    try:
        preference = (
            db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
        )

        if preference:
            # Update existing preference
            for key, value in kwargs.items():
                if hasattr(preference, key):
                    setattr(preference, key, value)
        else:
            # Create new preference with defaults
            defaults = {
                "bot_name": config.DEFAULT_BOT,
                "system_prompt": "",
                "temperature": 0.7,
            }
            preferences = {**defaults, **kwargs}
            preferences["user_id"] = user_id

            preference = UserPreference(**preferences)
            db.add(preference)

        db.commit()
    finally:
        db.close()


def add_message_to_history(
    user_id: int,
    role: str,
    content: str,
    bot_name: str,
    attachments: list[Attachment] | None = None,
):
    """Add a message to the conversation history."""
    db = get_db_session()
    # convert attachments to Dict type
    attachments_dict = []
    if attachments:
        attachments_dict = [
            {
                "url": attachment.url,
                "content_type": attachment.content_type,
                "name": attachment.name,
                "parsed_content": attachment.parsed_content,
            }
            for attachment in attachments
        ]

    try:
        message = ConversationHistory(
            user_id=user_id,
            role=role,
            content=content,
            bot_name=bot_name,
            timestamp=datetime.now(),
            attachments=attachments_dict,
        )
        db.add(message)
        db.commit()
    finally:
        db.close()


def get_conversation_history(
    user_id: int, limit: int = 10
) -> List[ConversationHistory]:
    """Get the recent conversation history for a user."""
    db = get_db_session()
    try:
        messages = (
            db.query(ConversationHistory)
            .filter(ConversationHistory.user_id == user_id)
            .order_by(ConversationHistory.timestamp.desc())
            .limit(limit)
            .all()
        )

        return messages
    finally:
        db.close()


def clear_conversation_history(user_id: int):
    """Clear the conversation history for a user."""
    db = get_db_session()
    try:
        db.query(ConversationHistory).filter(
            ConversationHistory.user_id == user_id
        ).delete()
        db.commit()
    finally:
        db.close()
