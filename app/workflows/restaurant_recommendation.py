from typing import Dict, Any, List, Annotated, TypedDict, Literal
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.workflows.base import ConversationState, get_llm, create_system_message, create_human_message, create_ai_message


class RecommendationState(ConversationState):
    """State for restaurant recommendation workflow."""
    preference_analysis: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    match_score: float


def initialize_state(location: str, preference: str, user_id: str = None) -> RecommendationState:
    """Initialize the state for restaurant recommendation workflow."""
    system_message = create_system_message(
        "You are a helpful AI assistant that specializes in food and restaurant recommendations. "
        "Your goal is to understand the user's preferences and provide tailored restaurant suggestions."
    )
    
    context = {
        "location": location,
        "user_id": user_id,
    }
    
    return {
        "messages": [system_message],
        "context": context,
        "preference_analysis": {},
        "recommendations": [],
        "match_score": 0.0,
    }


def analyze_preference(state: RecommendationState) -> RecommendationState:
    """Analyze the user's food preference."""
    llm = get_llm()
    
    # Get the user's preference from the context
    preference = state["context"].get("preference", "")
    location = state["context"].get("location", "")
    
    # Create a prompt for preference analysis
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert in analyzing food preferences. Extract key information from the user's request."),
        ("human", f"Location: {location}\nPreference: {preference}\n\nAnalyze this food preference and extract the following information:\n1. Cuisine types\n2. Dietary restrictions\n3. Price range preference\n4. Spice level preference\n5. Any specific dishes mentioned\n6. Any specific restaurant attributes mentioned (e.g., ambiance, service)\n\nFormat your response as a JSON object.")
    ])
    
    # Get the response from the LLM
    response = llm.invoke(prompt)
    
    # Update the state with the preference analysis
    try:
        # In a real application, we would parse the JSON response
        # For simplicity, we'll just use the raw text
        state["preference_analysis"] = {"raw_analysis": response.content}
        
        # Add the analysis to the messages
        state["messages"].append(create_ai_message(f"I've analyzed your preference: {response.content}"))
    except Exception as e:
        state["messages"].append(create_ai_message(f"I had trouble analyzing your preference. Error: {str(e)}"))
    
    return state


def generate_recommendations(state: RecommendationState) -> RecommendationState:
    """Generate restaurant recommendations based on the user's preference."""
    llm = get_llm()
    
    # Get the preference analysis and location from the state
    preference_analysis = state["preference_analysis"].get("raw_analysis", "")
    location = state["context"].get("location", "")
    preference = state["context"].get("preference", "")
    
    # Create a prompt for generating recommendations
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert restaurant recommender. Generate detailed restaurant recommendations based on the user's preference analysis."),
        ("human", f"Location: {location}\nPreference: {preference}\nPreference Analysis: {preference_analysis}\n\nGenerate 3 restaurant recommendations that match these preferences. For each restaurant, include:\n1. Name\n2. Rating (1-5)\n3. Price range ($-$$$$)\n4. Cuisine types\n5. Address\n6. A brief description of why it matches the user's preferences\n\nFormat your response as a JSON array of restaurant objects.")
    ])
    
    # Get the response from the LLM
    response = llm.invoke(prompt)
    
    # Update the state with the recommendations
    try:
        # In a real application, we would parse the JSON response and validate it
        # For simplicity, we'll just use the raw text
        state["recommendations"] = [{"raw_recommendations": response.content}]
        state["match_score"] = 0.92  # Mock match score
        
        # Add the recommendations to the messages
        state["messages"].append(create_ai_message(f"Here are my recommendations for you: {response.content}"))
    except Exception as e:
        state["messages"].append(create_ai_message(f"I had trouble generating recommendations. Error: {str(e)}"))
    
    return state


def decide_next_step(state: RecommendationState) -> Literal["analyze_preference", "generate_recommendations", "end"]:
    """Decide the next step in the workflow."""
    if not state["preference_analysis"]:
        return "analyze_preference"
    elif not state["recommendations"]:
        return "generate_recommendations"
    else:
        return "end"


def create_restaurant_recommendation_graph() -> StateGraph:
    """Create a graph for restaurant recommendation workflow."""
    workflow = StateGraph(RecommendationState)
    
    # Add nodes
    workflow.add_node("analyze_preference", analyze_preference)
    workflow.add_node("generate_recommendations", generate_recommendations)
    
    # Add edges
    workflow.add_conditional_edges(
        "",
        decide_next_step,
        {
            "analyze_preference": "analyze_preference",
            "generate_recommendations": "generate_recommendations",
            "end": END,
        },
    )
    
    workflow.add_edge("analyze_preference", "")
    workflow.add_edge("generate_recommendations", "")
    
    # Set the entry point
    workflow.set_entry_point("")
    
    return workflow


def run_restaurant_recommendation_workflow(location: str, preference: str, user_id: str = None) -> Dict[str, Any]:
    """Run the restaurant recommendation workflow."""
    # Initialize the state
    state = initialize_state(location, preference, user_id)
    
    # Add the user's preference to the messages
    state["messages"].append(create_human_message(f"I'm in {location} and {preference}"))
    
    # Add the preference to the context
    state["context"]["preference"] = preference
    
    # Create the workflow
    workflow = create_restaurant_recommendation_graph()
    
    # Compile the workflow
    app = workflow.compile()
    
    # Run the workflow
    result = app.invoke(state)
    
    return result
