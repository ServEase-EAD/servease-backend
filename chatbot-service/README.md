# Chatbot Service - ServEase

AI-powered chatbot service using OpenRouter API integration.

## Features

- AI chat completions using OpenRouter
- Session-based conversation history
- Multiple AI model support (GPT-4, Claude, etc.)
- Conversation persistence in database
- RESTful API endpoints

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Required environment variables:

- `OPENROUTER_API_KEY` - Your OpenRouter API key (get it from https://openrouter.ai/)
- `CHATBOT_DB_NAME` - Database name
- `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` - Database credentials

### 3. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 5. Start the Server

```bash
python manage.py runserver 8007
```

## API Endpoints

### Base URL

`http://localhost:8007/api/v1/chatbot/`

### 1. Send Chat Message

**POST** `/api/v1/chatbot/chat/`

Request body:

```json
{
  "message": "What is ServEase?",
  "session_id": "optional-session-id",
  "model": "openai/gpt-4o"
}
```

Response:

```json
{
  "session_id": "uuid-session-id",
  "message": "AI response here...",
  "role": "assistant",
  "timestamp": "2025-10-31T10:30:00Z"
}
```

### 2. List All Sessions

**GET** `/api/v1/chatbot/sessions/`

Response:

```json
[
  {
    "id": 1,
    "session_id": "uuid",
    "user_id": 1,
    "created_at": "2025-10-31T10:00:00Z",
    "updated_at": "2025-10-31T10:30:00Z",
    "is_active": true,
    "messages": [...]
  }
]
```

### 3. Get Specific Session

**GET** `/api/v1/chatbot/session/{session_id}/`

### 4. Clear Session Messages

**POST** `/api/v1/chatbot/session/{session_id}/clear/`

### 5. Delete Session

**DELETE** `/api/v1/chatbot/session/{session_id}/delete/`

### 6. Health Check

**GET** `/health/`

## Supported AI Models

You can specify any OpenRouter-supported model:

- `openai/gpt-4o` (default)
- `openai/gpt-4-turbo`
- `anthropic/claude-3-opus`
- `anthropic/claude-3-sonnet`
- `google/gemini-pro`
- `meta-llama/llama-3-70b-instruct`

See [OpenRouter Models](https://openrouter.ai/models) for full list.

## Usage Example

### Using cURL

```bash
# Start a new conversation
curl -X POST http://localhost:8007/api/v1/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! What can you help me with?"
  }'

# Continue conversation
curl -X POST http://localhost:8007/api/v1/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me more about that",
    "session_id": "session-id-from-previous-response"
  }'
```

### Using Python requests

```python
import requests

url = "http://localhost:8007/api/v1/chatbot/chat/"
data = {
    "message": "What is the weather like today?",
    "model": "openai/gpt-4o"
}

response = requests.post(url, json=data)
print(response.json())
```

## Database Schema

### ChatSession

- `user_id` - User identifier
- `session_id` - Unique session UUID
- `created_at` - Session creation timestamp
- `updated_at` - Last update timestamp
- `is_active` - Session status

### ChatMessage

- `session` - Foreign key to ChatSession
- `role` - Message role (user/assistant/system)
- `content` - Message content
- `timestamp` - Message timestamp
- `token_count` - Optional token count

## Development Notes

- The service maintains conversation context by storing message history
- Each session can have unlimited messages
- Sessions are user-specific (requires authentication integration)
- API responses are JSON formatted
- CORS is enabled for frontend integration

## Integration with Other Services

This service can be integrated with:

- Authentication Service for user management
- Customer Service for customer-specific queries
- Appointment Service for booking assistance
- Any other microservice via REST API calls

## Future Enhancements

- [ ] Streaming responses
- [ ] Token usage tracking
- [ ] Cost estimation per conversation
- [ ] Multi-language support
- [ ] Voice input/output
- [ ] Context from other services
- [ ] Custom system prompts per session

## Troubleshooting

### "Invalid API Key" error

- Check your `OPENROUTER_API_KEY` in `.env`
- Verify your API key is active on OpenRouter

### Database connection errors

- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure database exists

### Port already in use

- Change the port: `python manage.py runserver 8008`
- Or kill the process using port 8007

## License

Part of the ServEase platform.
