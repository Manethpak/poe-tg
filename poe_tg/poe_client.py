from typing import Literal, Optional, cast
import fastapi_poe as fp
from poe_tg import config
from poe_tg.db.database import (
    get_conversation_history,
    add_message_to_history,
    get_user_preference,
)
from telegram import Update, File
from telegram.ext import ContextTypes


async def get_poe_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Get response from Poe API with conversation history."""
    if not update.effective_user or not update.message:
        return "Sorry, I encountered an error: Invalid user or message"

    if not update.message.caption and not update.message.text:
        return "Sorry, I encountered an error: Could not find message text, please attach a caption when sending a file/photo"

    try:
        # Get recent conversation history
        user_id = update.effective_user.id
        preference = get_user_preference(user_id)

        # Extract values from the preference object safely
        system_prompt = str(preference.system_prompt)
        temperature = float(preference.temperature)  # type: ignore
        bot_name = str(preference.bot_name)
        message_text = update.message.text or update.message.caption or ""

        # check message if there is any file attached
        file_paths: list[File] = []
        if update.message.photo or update.message.document:
            if update.message.photo:
                file = await context.bot.get_file(update.message.photo[-1].file_id)
            elif update.message.document:
                file = await context.bot.get_file(update.message.document.file_id)
            file_paths.append(file)

        # Get conversation history
        attachments = [
            fp.upload_file_sync(file_url=file.file_path, api_key=config.POE_API_KEY)
            for file in file_paths
        ]
        messages = build_message(user_id, system_prompt, message_text, attachments)

        # Use the direct API approach as shown in Poe documentation
        full_response = ""
        async for partial in fp.get_bot_response(
            messages=messages,
            bot_name=bot_name,
            api_key=config.POE_API_KEY,
            temperature=temperature,
        ):
            full_response += partial.text

        # Save the conversation to history
        add_message_to_history(user_id, "user", message_text, bot_name, attachments)
        add_message_to_history(user_id, "bot", full_response, bot_name)

        return full_response
    except Exception as e:
        config.logger.error(f"Error getting response from Poe: {e}")
        return f"Sorry, I encountered an error: {str(e)}"


def build_message(
    user_id: int,
    system_prompt: str,
    message_text: str,
    attachments: Optional[list[fp.Attachment]] = None,
) -> list[fp.ProtocolMessage]:
    history = get_conversation_history(user_id, limit=10)

    messages = []

    if system_prompt:
        messages.append(fp.ProtocolMessage(role="system", content=system_prompt))

    for msg in history:
        role = cast(Literal["system", "user", "bot"], msg.role)
        content = str(msg.content)
        historic_attachment = []
        if msg.attachments:  # type: ignore
            historic_attachment = [
                fp.Attachment(
                    url=a["url"], content_type=a["content_type"], name=a["name"], parsed_content=a["parsed_content"]  # type: ignore
                )
                for a in msg.attachments
            ]

        messages.append(
            fp.ProtocolMessage(
                role=role, content=content, attachments=historic_attachment
            )
        )

    messages.append(
        fp.ProtocolMessage(
            role="user",
            content=message_text,
            sender_id=str(user_id),
            attachments=attachments or [],
        )
    )

    return messages
