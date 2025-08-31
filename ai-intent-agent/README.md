# Intent Agent

Intent Agent is an AI-powered service that processes natural language queries to detect user intent and extract entities for hotel booking conversations. It's a key component of the GraphMata ecosystem by Prometa AI, designed to handle the natural language understanding portion of conversational AI interactions.

## Tech Stack

- **Backend**: Python 3.11, FastAPI, Uvicorn
- **AI/ML Framework**: LangChain, LangGraph, OpenAI
- **State Management**: Redis (Pub/Sub)
- **Deployment**: Docker, Google Cloud Run
- **Secret Management**: Google Cloud Secret Manager
- **Dependencies Management**: pip-tools
- **Authentication**: Header-based authentication system

## Folder Structure

```
intent-agent/
├── app.py                    # Main application entry point
├── src/                      # Source code directory
│   ├── agent/                # Intent processing agent implementation
│   │   ├── __init__.py
│   │   └── intent_agent.py   # Core intent classification logic
│   ├── config/               # Application configuration
│   │   ├── __init__.py
│   │   └── config.py         # Environment settings and configurations
│   ├── dependency/           # FastAPI dependencies
│   │   ├── __init__.py
│   │   └── bizigo_headers.py # Header validation and extraction
│   ├── logger/               # Logging utilities
│   │   └── __init__.py
│   ├── promt_library/        # LLM prompt templates
│   │   ├── __init__.py
│   │   └── promt_lib.py      # Intent classification prompt templates
│   ├── routers/              # FastAPI route definitions
│   │   ├── __init__.py
│   │   ├── health_router.py  # Health check endpoint
│   │   └── process_querry_router.py # Intent processing endpoint
│   ├── schemas/              # Pydantic data models
│   │   ├── __init__.py
│   │   ├── header_schema.py  # Request header validation schemas
│   │   └── schemas.py        # Request/response data models
│   └── util/                 # Utility functions
│       ├── __init__.py
│       └── utilities.py      # Redis, LLM and context utilities
├── Dockerfile                # Container definition
├── requirements.in           # Project dependencies
├── cloudbuild.yaml           # Google Cloud Build configuration
└── .env                      # Environment variables (not tracked in git)
```

## Installation

### Prerequisites
- Python 3.11+
- Redis server
- OpenAI API key

### Local Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd intent-agent
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install pip-tools
   pip-compile requirements.in --output-file=requirements.txt
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the project root with the following variables:
   ```
   OPENAI=<your-openai-api-key>
   LANGSMITH_API_KEY=<your-langsmith-api-key>
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_LOG=service-logs
   REDIS_PUBLISH=intent-state-update
   REDIS_DB=15
   ```

5. **Start the application**
   ```bash
   python app.py
   ```
   The service will be available at http://localhost:8000

### Docker Setup

1. **Build the Docker image**
   ```bash
   docker build -t intent-agent:latest .
   ```

2. **Run the container**
   ```bash
   docker run -p 8080:8080 --env-file .env_studio intent-agent:latest
   ```

## Usage & API Examples

### Process Query Endpoint

This is the main endpoint for processing natural language queries.

```bash
curl -X POST http://localhost:8000/process_query \
  -H "Content-Type: application/json" \
  -H "Applicationid: 3334" \
  -H "Userid: 24115" \
  -H "LanguageCode: tr" \
  -H "Bearer: your-auth-token" \
  -d '{
    "user_input": "Istanbulda Topkapı civarında bir otel bul",
    "session_id": "33",
    "message_id": "1",
    "sequence": 1,
    "trace_id": 1
  }'
```

**Response**: The endpoint will return a 200 OK status code upon successful processing. Results are published to Redis PubSub and not returned directly in the response.

### Health Check Endpoint

```bash
curl -X GET http://localhost:8000/health
```

Response:
```json
{
  "status": "ok"
}
```

## Conversation Context and State Management

The service maintains conversation context by retrieving previous conversational data from Redis. This is crucial for maintaining context across multiple user interactions.

When an intent is classified, the service:

1. Pulls existing conversation context from Redis using the session ID key pattern: `conversation:{session_id}`
2. The stored conversation data contains:
   - Previous user messages and system responses
   - Already filled slots/entities
   - Conversation history timestamps
   - Language preferences

Example of conversation context stored in Redis:
```json
{
  "intent": {
    "entities": {
      "LLM_outputText": "10 Haziran'da girerim 15 Haziran'da çıkarım!",
      "checkinDate": "10 Haziran", 
      "checkoutDate": "15 Haziran"
    }
  },
  "user_input": {
    "text": "10 haziranda gireirm 15 haziranda çıkarım!",
    "language": "tr"
  },
  "conversation": "User [2025-06-16 13:38:21]: Istanbulda Topkapı civarında bir otel bul!\nChatbot [2025-06-16 13:38:24]: Hangi tarihler arasında kaç kişi ve kaç oda için, kaç yıldızlı bir otelde, hangi özelliklere sahip ve hangi fiyat aralığında konaklamak istersiniz?\nUser [2025-06-16 13:39:20]: 10 haziranda gireirm 15 haziranda çıkarım!",
  "chat_data": {
    "filled_slots": {
      "checkinDate": "10 Haziran",
      "checkoutDate": "15 Haziran",
      "location": "Istanbul Topkapı"
    }
  }
}
```

This data is merged with the new intent classification to provide continuity in the conversation flow.

## Redis PubSub Message Format

The service publishes intent processing results to Redis in the following format:

```json
{
  "session_id": "33",
  "message_id": "1",
  "timestamp": "2025-06-16T14:01:10.715",
  "version": "1.0.1",
  "trace_info": {
    "trace_id": 4,
    "flow": "hotel_list_followup",
    "sequence": 5,
    "retry_count": 0
  },
  "metadata": {
    "user_id": "222",
    "application_id": "333",
    "language": "tr",
    "source_service": "intent-agent",
    "event_type": "state_update"
  },
  "state": {
    "current": {
      "user_input": {
        "text": "10 şuabt girirm 20 şubat çıkarım!",
        "language": "tr"
      },
      "intent_phase": {
        "status": "classified",
        "intent": "hotel_list_followup",
        "confidence": 0.8,
        "entities": {
          "LLM_outputText": "10 Şubat girerim 20 Şubat çıkarım!",
          "location": "Istanbul Topkapı",
          "hotelNameQuery": "",
          "NumberOfPeople": "",
          "NumberOfRooms": "",
          "checkinDate": "10 Şubat",
          "checkoutDate": "20 Şubat",
          "poi": "",
          "hotelStarQuery": "",
          "featureQuery": "",
          "price": ""
        }
      }
    },
    "transition": "intent_classified"
  }
}
```

## API Endpoints Documentation

### Health Check
- **Endpoint**: GET `/health`
- **Description**: Check if the service is running
- **Response**: 200 OK with status: "ok"

### Process Query
- **Endpoint**: POST `/process_query`
- **Description**: Process a natural language query to detect intent and extract entities
- **Headers**:
  - `Applicationid`: Client application ID
  - `Userid`: User ID
  - `LanguageCode`: Language code (e.g., "en", "tr")
  - `Bearer`: Authentication token
- **Request Body**:
  ```json
  {
    "user_input": "string",
    "session_id": "string",
    "message_id": "string",
    "sequence": 0,
    "trace_id": 0
  }
  ```
- **Response**: 200 OK (results published to Redis PubSub)
- **Error Codes**:
  - 400: Bad Request (missing parameters)
  - 500: Internal Server Error

## Running Tests

To run the test suite:

```bash
# Run all tests
python -m pytest

# Run tests with coverage report
python -m pytest --cov=src
```

## Project Architecture

### System Components

Intent Agent uses a combination of FastAPI for API handling and LangGraph for orchestrating intent classification:

1. **API Layer** (routers): Handles HTTP requests and responses
2. **Agent Layer** (intent_agent): Contains the core business logic for intent classification
3. **Context Management Layer** (utilities): Manages conversation context between requests
4. **State Publishing Layer**: Publishes results to Redis PubSub

### Processing Flow

The intent classification process follows these steps:

1. **Request Reception**: FastAPI endpoint receives a query with user input
2. **Context Retrieval**: System retrieves conversation context from Redis
3. **Intent Classification**: LangGraph processes the user input with LLM
4. **Entity Extraction**: System identifies entities like location, dates, etc.
5. **Context Update**: New entities are merged with previous conversation context
6. **State Publication**: Results are published to Redis PubSub channel
7. **Response**: System returns success/error response to client

### Component Interactions

```
                            ┌────────────────────┐
                            │                    │
                            │  Bizigo BFF   │
                            │                    │
                            └────────┬───────────┘
                                     │
                                     ▼
┌────────────────────┐      ┌────────────────────┐
│                    │      │                    │
│  Redis Context     │◄─────┤  Intent Agent      │
│  Storage           │      │  (LangGraph)       │
│                    │      │                    │
└─────────┬──────────┘      └────────┬───────────┘
          │                          │
          │                          ▼
          │                 ┌────────────────────┐
          │                 │                    │
          └────────────────►│  Redis PubSub      │
                            │                    │
                            └────────────────────┘
                                     │
                                     ▼
                            ┌────────────────────┐
                            │  Other Services    │
                            │ (orchestrator,..)  │
                            └────────────────────┘
```

## Intent Classification Details

The Intent Agent is capable of identifying the following intents:

- `hotel_list`: User is searching for a list of hotels
- `hotel_detail`: User is requesting details about a specific hotel
- `hotel_list_followup`: User is providing additional information for a hotel search
- `hotel_detail_followup`: User is requesting more specific details about a hotel
- `hotel_list_confirmation_yes`/`hotel_list_confirmation_no`: User is confirming or rejecting a hotel list option
- `hotel_detail_confirmation_yes`/`hotel_detail_confirmation_no`: User is confirming or rejecting a hotel detail option
- `out_of_scope`: Query doesn't match any supported intent

For each intent, the agent extracts relevant entities such as:

- `location`: City or specific area
- `checkinDate`/`checkoutDate`: Stay dates
- `NumberOfPeople`/`NumberOfRooms`: Guest and room details
- `hotelStarQuery`: Star rating preferences
- `featureQuery`: Hotel features (pool, breakfast, etc.)
- `price`: Price range preferences
- `poi`: Points of interest nearby

## Contributing Guidelines

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add some amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

Please ensure your code follows the project's style guidelines and includes appropriate tests.

## License

Copyright © 2025 Prometa AI. All rights reserved.

This is proprietary software. Unauthorized copying or distribution is prohibited.

---

© 2025 Prometa AI. All Rights Reserved.
