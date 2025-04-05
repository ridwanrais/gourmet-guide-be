from typing import Any, Dict, List, Optional, TypedDict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from openai import OpenAI

from src.config import settings


class ConversationState(TypedDict):
    """Type for the state of the conversation."""

    messages: List[Dict[str, Any]]
    context: Dict[str, Any]


def get_openai_client():
    """Get the OpenAI client configured for OpenRouter."""
    return OpenAI(
        base_url=settings.OPENROUTER_BASE_URL,
        api_key=settings.OPENROUTER_API_KEY,
    )


def get_llm(model_name: str = None):
    """Get the language model using OpenRouter with Deepseek R1."""
    # This is kept for backward compatibility but will use the direct OpenAI SDK approach
    # in the actual implementation
    return get_openai_client()


def create_system_message(content: str) -> Dict[str, Any]:
    """Create a system message."""
    return {"role": "system", "content": content}


def create_human_message(content: str) -> Dict[str, Any]:
    """Create a human message."""
    return {"role": "user", "content": content}


def create_ai_message(content: str) -> Dict[str, Any]:
    """Create an AI message."""
    return {"role": "assistant", "content": content}


def get_last_human_message(state: ConversationState) -> Optional[Dict[str, Any]]:
    """Get the last human message from the state."""
    for message in reversed(state["messages"]):
        if message.get("role") == "user":
            return message
    return None


def get_last_ai_message(state: ConversationState) -> Optional[Dict[str, Any]]:
    """Get the last AI message from the state."""
    for message in reversed(state["messages"]):
        if message.get("role") == "assistant":
            return message
    return None
