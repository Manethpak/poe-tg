import fastapi_poe as fp
from poe_tg import config
from poe_tg.db.database import get_conversation_history, add_message_to_history

# TODO: to fp.get_get_final_response using fp.QueryRequest to build request with proper user_id,conversation_id, message_id
# TODO: handle file upload


async def get_poe_response(user_message: str, bot_name: str, user_id: int) -> str:
    """Get response from Poe API with conversation history."""
    try:
        # Get recent conversation history
        history = get_conversation_history(user_id, limit=5)

        # Create messages list with history and new user message
        messages = []
        # for msg in history:
        #     messages.append(
        #         fp.ProtocolMessage(role=msg["role"], content=msg["content"])
        #     )

        # Add the current user message
        messages.append(fp.ProtocolMessage(role="user", content=user_message))

        # Save the user message to history
        add_message_to_history(user_id, "user", user_message, bot_name)

        # If no history, just use the current message
        if not messages:
            messages = [fp.ProtocolMessage(role="user", content=user_message)]
        print([msg.model_dump().get("content") for msg in messages])
        full_response = ""
        async for partial in fp.get_bot_response(
            messages=messages,
            bot_name=bot_name,
            api_key=config.POE_API_KEY,
        ):
            full_response += partial.text

        # Save the bot response to history
        # add_message_to_history(user_id, "bot", full_response, bot_name)

        return full_response
    except Exception as e:
        config.logger.error(f"Error getting response from Poe: {e}")
        return f"Sorry, I encountered an error: {str(e)}"
