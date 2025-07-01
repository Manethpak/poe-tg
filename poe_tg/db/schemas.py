from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserPreferenceBase(BaseModel):
    bot_name: str
    system_prompt: str = ""
    temperature: float = 0.7


class UserPreferenceCreate(UserPreferenceBase):
    user_id: int


class UserPreferenceUpdate(BaseModel):
    bot_name: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: Optional[float] = None


class ConversationMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime
    bot_name: str


class ConversationHistory(BaseModel):
    user_id: int
    messages: list[ConversationMessage]
