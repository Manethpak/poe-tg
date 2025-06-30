from typing import List

from telegram.ext import ContextTypes
from . import config


async def catch_error(context: ContextTypes.DEFAULT_TYPE) -> str:
    """Catch all errors and log them."""
    config.logger.error(f"Error: {context.error}")
    return "Sorry, something went wrong while processing your request. Please try again later."


def split_message(text: str, limit: int = config.TELEGRAM_MESSAGE_LIMIT) -> List[str]:
    """Split a message into chunks that fit within Telegram's character limit."""
    if len(text) <= limit:
        return [text]

    chunks = []
    current_chunk = ""

    # Try to split on paragraph breaks first
    paragraphs = text.split("\n\n")

    for paragraph in paragraphs:
        # If a single paragraph is too long, we'll need to split it
        if len(paragraph) > limit:
            # Split the paragraph into sentences
            sentences = paragraph.replace(". ", ".\n").split("\n")

            for sentence in sentences:
                # If a single sentence is too long, we'll need to split it by character
                if len(sentence) > limit:
                    while sentence:
                        # Find a good breaking point (preferably at a space)
                        if len(sentence) <= limit:
                            chunk_end = len(sentence)
                        else:
                            chunk_end = sentence[:limit].rfind(" ")
                            if chunk_end == -1:  # No space found, just cut at the limit
                                chunk_end = limit

                        # Add this chunk to our result
                        if (
                            current_chunk
                            and len(current_chunk) + len(sentence[:chunk_end]) + 1
                            > limit
                        ):
                            chunks.append(current_chunk)
                            current_chunk = sentence[:chunk_end]
                        else:
                            if current_chunk:
                                current_chunk += "\n"
                            current_chunk += sentence[:chunk_end]

                        # Move to the next part of the sentence
                        sentence = sentence[chunk_end:].lstrip()
                else:
                    # This sentence fits within the limit
                    if current_chunk and len(current_chunk) + len(sentence) + 1 > limit:
                        chunks.append(current_chunk)
                        current_chunk = sentence
                    else:
                        if current_chunk:
                            current_chunk += "\n"
                        current_chunk += sentence
        else:
            # This paragraph fits within the limit
            if current_chunk and len(current_chunk) + len(paragraph) + 2 > limit:
                chunks.append(current_chunk)
                current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += "\n\n"
                current_chunk += paragraph

    # Don't forget the last chunk
    if current_chunk:
        chunks.append(current_chunk)

    return chunks
