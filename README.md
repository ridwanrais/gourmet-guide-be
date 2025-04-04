# Gourmet Guide API

A FastAPI backend that integrates with LangGraph for conversational AI workflows, uses Pydantic for data validation, and stores time-series data in TimescaleDB. Built following clean architecture principles for better maintainability and testability.

## Features

- **Clean Architecture**: Organized into domain, application, adapters, infrastructure, and presentation layers for clear separation of concerns.
- **FastAPI Setup**: Asynchronous endpoints for handling AI interactions and time-series data with dependency injection for database connections.
- **LangGraph Integration**: Processes user queries through a multi-step conversation flow and stores results in the database.
- **Pydantic Models**: Strictly validates request/response data based on the API contract.
- **TimescaleDB Integration**: Efficiently stores and queries time-series data like chat history and AI usage statistics.
- **OpenRouter Integration**: Uses the Deepseek R1 model from OpenRouter for high-quality AI responses.

## Project Structure

```
gourmet-guide-api/
├── src/
│   ├── domain/
│   │   ├── models.py           # Database models and entities
│   │   └── value_objects.py    # Pydantic models for request/response validation
│   ├── application/
│   │   ├── services.py         # Business logic for preferences and location
│   │   ├── workflows.py        # Base LLM configuration
│   │   └── restaurant_workflow.py  # Restaurant recommendation workflow
│   ├── adapters/
│   │   └── repositories.py     # Repository pattern for database operations
│   ├── infrastructure/
│   │   ├── database.py         # Database connection and session management
│   │   └── init_db.py          # Database initialization
│   ├── presentation/
│   │   └── routes/
│   │       ├── location.py     # Location endpoints
│   │       ├── preferences.py  # Preferences endpoints
│   │       └── restaurants.py  # Restaurant recommendations endpoints
│   └── main.py                 # FastAPI application setup
├── .env                        # Environment variables
├── docker-compose.yml          # Docker setup for TimescaleDB
├── requirements.txt            # Python dependencies
└── run.py                      # Application entry point
```

## Requirements

- Python 3.11 (LTS version recommended for best compatibility with dependencies)
- Docker and Docker Compose (for TimescaleDB)
- OpenRouter API key

## Setup

1. **Clone the repository**

2. **Set up environment variables**

   Copy the `.env.example` file to `.env` and update the values:

   ```
   # Database Configuration
   DB_HOST=localhost
   DB_PORT=5432
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_NAME=gourmet_guide

   # API Configuration
   API_V1_PREFIX=/v1

   # OpenRouter Configuration
   # Replace with your actual OpenRouter API key from https://openrouter.ai/keys
   OPENROUTER_API_KEY=your_openrouter_api_key
   OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
   OPENROUTER_MODEL=deepseek/deepseek-chat-r1

   # Security
   SECRET_KEY=your_secret_key_for_jwt
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

3. **Start TimescaleDB using Docker**

   ```bash
   docker-compose up -d
   ```

4. **Create and activate a Python virtual environment**

   ```bash
   # Install Python 3.11 if not already installed
   # On macOS with Homebrew:
   # brew install python@3.11

   # Create virtual environment with Python 3.11
   python3.11 -m venv venv
   source venv/bin/activate
   ```

5. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

6. **Run ngrok for local development**

   ```bash
   ngrok http --url=catfish-right-tick.ngrok-free.app 8080 --host-header=rewrite
   ```

7. **Run the application**

   ```bash
   python run.py
   ```

   The API will be available at `http://localhost:8080`.

8. **Testing OpenRouter Integration**

   If you want to test just the OpenRouter integration with the Deepseek R1 model:

   ```bash
   # Make sure you have your OpenRouter API key in the .env file
   source venv/bin/activate
   pip install requests python-dotenv
   python test_openrouter.py
   ```

## API Endpoints

### Location Endpoints

- `POST /v1/location/geocode`: Convert address to coordinates
- `POST /v1/location/reverse-geocode`: Convert coordinates to address

### Preferences Endpoints

- `GET /v1/preferences/suggestions`: Get food preference suggestions

### Restaurants Endpoints

- `POST /v1/restaurants/recommendations`: Get restaurant recommendations based on location and preferences

## API Documentation

Once the API is running, you can access the interactive documentation:

- Swagger UI: `http://localhost:8080/v1/docs`
- ReDoc: `http://localhost:8080/v1/redoc`

## Clean Architecture

This project follows clean architecture principles with the following layers:

1. **Domain Layer**: Contains business entities and value objects with no dependencies on other layers.
2. **Application Layer**: Contains business logic and use cases, depends only on the domain layer.
3. **Adapters Layer**: Implements interfaces between the application and infrastructure layers.
4. **Infrastructure Layer**: Contains database configuration and external services.
5. **Presentation Layer**: Contains API routes and controllers with no business logic.

This architecture provides better separation of concerns, testability, and maintainability.

## Troubleshooting

If you encounter issues:

1. **Database Connection**

   - Ensure TimescaleDB container is running: `docker ps`
   - Check logs: `docker logs gourmet_guide_timescaledb`

2. **OpenRouter API**

   - Verify your API key is correct
   - Check if you have sufficient credits on your OpenRouter account

3. **Python Dependencies**
   - If you encounter build errors, ensure you have the necessary system dependencies installed
   - For macOS: `brew install postgresql`
