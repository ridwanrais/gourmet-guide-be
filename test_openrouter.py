import json
import os

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get OpenRouter API key from environment variables
api_key = os.getenv("OPENROUTER_API_KEY")

# Define the API endpoint
api_url = "https://openrouter.ai/api/v1/chat/completions"

# Define headers
headers = {
    "Authorization": f"Bearer {api_key}" if api_key else "",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://gourmetguide.ai",  # Optional, for tracking
    "X-Title": "Gourmet Guide AI",  # Optional, for tracking
}

# Define the request payload
payload = {
    "model": "deepseek/deepseek-chat-r1",
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful food recommendation assistant. Generate diverse and creative food preference suggestions that users might want to ask about.",
        },
        {
            "role": "user",
            "content": "Generate 5 different food preference suggestions. These should be phrased as if a user is asking for food recommendations. Make them diverse in terms of cuisine types, dietary restrictions, price ranges, and specific needs (like quick meals, healthy options, etc.).",
        },
    ],
    "temperature": 0.7,
    "max_tokens": 300,
}


def test_openrouter():
    """Test OpenRouter with Deepseek R1 model."""
    if not api_key:
        print("\nError: OpenRouter API key not found!")
        print("Please add your OpenRouter API key to the .env file:")
        print("OPENROUTER_API_KEY=your_actual_api_key")
        return False

    try:
        # Make the API request
        print("Sending request to OpenRouter API...")
        response = requests.post(api_url, headers=headers, json=payload)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the response
            result = response.json()

            # Extract and print the generated text
            generated_text = result["choices"][0]["message"]["content"]
            print("\nGenerated Food Preference Suggestions:")
            print("-------------------------------------")
            print(generated_text)
            print("\nAPI Response Details:")
            print("---------------------")
            print(json.dumps(result, indent=2))

            return True
        else:
            print(f"\nError: {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print(f"\nException: {str(e)}")
        return False


if __name__ == "__main__":
    print("Testing OpenRouter with Deepseek R1 model...")
    test_openrouter()
