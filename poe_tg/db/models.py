from sqlalchemy import Column, Integer, String, Text, Float, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class UserPreference(Base):
    __tablename__ = "user_preferences"

    user_id = Column(BigInteger, primary_key=True)
    bot_name = Column(String(255), nullable=False)
    system_prompt = Column(Text, default="")
    temperature = Column(Float, default=0.7)


class ConversationHistory(Base):
    __tablename__ = "conversation_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=func.now())
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    bot_name = Column(String(255), nullable=False)
