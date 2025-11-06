# Chatbot Service Setup Instructions

## Quick Setup Steps

### 1. Navigate to chatbot service directory

```bash
cd chatbot-service
```

### 2. Install required packages

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install Django==5.2.6
pip install djangorestframework==3.15.2
pip install django-cors-headers==4.4.0
pip install python-decouple==3.8
pip install psycopg[binary]==3.2.3
pip install requests==2.31.0
```

### 3. Create .env file

```bash
# Create .env from example
cp .env.example .env
```

Then edit `.env` and add your Google Gemini API key:

```env
GEMINI_API_KEY=your_actual_google_gemini_api_key_here
```

Get your API key from the Google Cloud Console and enable the Generative AI API.

### 4. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create superuser (optional, for admin access)

```bash
python manage.py createsuperuser
```

### 6. Start the server

```bash
python manage.py runserver 8008
```

## Testing the API

### Test 1: Health Check

```bash
curl http://localhost:8008/health/
```

Expected response:

```json
{ "status": "healthy", "service": "chatbot" }
```

### Test 2: Send a chat message

```bash
curl -X POST http://localhost:8008/api/v1/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Hello, what can you do?\"}"
```

### Test 3: Using PowerShell (Windows)

```powershell
$body = @{
    message = "What is ServEase?"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8008/api/v1/chatbot/chat/" -Method Post -Body $body -ContentType "application/json"
```

## Project Structure

```
chatbot-service/
├── chatbot/                    # Main app
│   ├── __init__.py
│   ├── admin.py               # Django admin configuration
│   ├── apps.py                # App configuration
│   ├── models.py              # ChatSession and ChatMessage models
│   ├── serializers.py         # DRF serializers
│   ├── views.py               # API views
│   ├── urls.py                # URL routing
│   ├── gemini_client.py   # Google Gemini API client
│   └── migrations/            # Database migrations
├── chatbot_service/           # Project settings
│   ├── __init__.py
│   ├── settings.py            # Django settings
│   ├── urls.py                # Main URL configuration
│   ├── wsgi.py
│   └── asgi.py
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .env                      # Your actual environment variables (create this)
└── README.md                 # Documentation

```

## API Endpoints Summary

| Method | Endpoint                               | Description                        |
| ------ | -------------------------------------- | ---------------------------------- |
| POST   | `/api/v1/chatbot/chat/`                | Send message and get AI response   |
| GET    | `/api/v1/chatbot/sessions/`            | List all chat sessions             |
| GET    | `/api/v1/chatbot/session/{id}/`        | Get specific session with messages |
| POST   | `/api/v1/chatbot/session/{id}/clear/`  | Clear session messages             |
| DELETE | `/api/v1/chatbot/session/{id}/delete/` | Delete (deactivate) session        |
| GET    | `/health/`                             | Service health check               |

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'rest_framework'"

**Solution:** Install djangorestframework

```bash
pip install djangorestframework
```

### Issue: "No module named 'requests'"

**Solution:** Install requests

```bash
pip install requests
```

### Issue: "No module named 'decouple'"

**Solution:** Install python-decouple

```bash
pip install python-decouple
```

### Issue: Database connection error

**Solution:** Make sure PostgreSQL is running or use SQLite for development by updating `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### Issue: Port 8008 already in use

**Solution:** Use a different port

```bash
python manage.py runserver 8008
```

## Development Tips

1. **View admin panel**: After creating superuser, visit http://localhost:8008/admin/

2. **Check logs**: Django shows detailed error messages in the console

3. **Test with different models**: Change the model in your API request:

   ```json
   {
     "message": "Hello",
     "model": "anthropic/claude-3-sonnet"
   }
   ```

4. **Monitor conversations**: Check the admin panel to see saved sessions and messages

5. **Debug mode**: Make sure `DEBUG=True` in settings.py during development

## Next Steps

- Integrate with authentication service for user management
- Add context from other microservices (customer data, appointments, etc.)
- Implement streaming responses for real-time chat
- Add rate limiting for API protection
- Set up monitoring and logging

## Support

For issues or questions, refer to:

- Django docs: https://docs.djangoproject.com/
- DRF docs: https://www.django-rest-framework.org/
  -- Google Generative AI docs: https://cloud.google.com/generative-ai
