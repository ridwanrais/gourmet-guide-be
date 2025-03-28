from typing import Dict, Any, TypedDict, List, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from app.core.config import settings


class ConversationState(TypedDict):
    """Type for the state of the conversation."""
    messages: List[Dict[str, Any]]
    context: Dict[str, Any]


def get_llm(model_name: str = None):
    """Get the language model using OpenRouter with Deepseek R1."""
    model = model_name or settings.OPENROUTER_MODEL
    
    return ChatOpenAI(
        model=model,
        temperature=0.7,
        openai_api_key=settings.OPENROUTER_API_KEY,
        openai_api_base=settings.OPENROUTER_BASE_URL,
        headers={
            "HTTP-Referer": "https://gourmetguide.ai",  # Optional, for tracking
            "X-Title": "Gourmet Guide AI"  # Optional, for tracking
        }
    )


def create_system_message(content: str) -> Dict[str, Any]:
    """Create a system message."""
    return SystemMessage(content=content).dict()


def create_human_message(content: str) -> Dict[str, Any]:
    """Create a human message."""
    return HumanMessage(content=content).dict()


def create_ai_message(content: str) -> Dict[str, Any]:
    """Create an AI message."""
    return AIMessage(content=content).dict()


def get_last_human_message(state: ConversationState) -> Optional[str]:
    """Get the last human message from the state."""
    for message in reversed(state["messages"]):
        if message.get("type") == "human":
            return message.get("content")
    return None


def get_last_ai_message(state: ConversationState) -> Optional[str]:
    """Get the last AI message from the state."""
    for message in reversed(state["messages"]):
        if message.get("type") == "ai":
            return message.get("content")
    return None
