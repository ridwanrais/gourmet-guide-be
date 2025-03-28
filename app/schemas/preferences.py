from pydantic import BaseModel, Field
from typing import List


class SuggestionsResponse(BaseModel):
    suggestions: List[str] = Field(
        ...,
        example=[
            "I feel like eating something spicy and cheap",
            "Recommend a healthy lunch option",
            "What's a good vegetarian restaurant nearby?",
            "I want something quick and filling",
            "Show me the best-rated restaurants"
        ]
    )
