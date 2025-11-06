import requests
import json
from django.conf import settings
from decouple import config


class OpenRouterClient:
    """Client for interacting with OpenRouter API"""

    def __init__(self):
        self.api_key = config('OPENROUTER_API_KEY', default='')
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.site_url = config('SITE_URL', default='http://localhost:8008')
        self.site_name = config('SITE_NAME', default='ServEase Chatbot')

    def create_chat_completion(self, messages, model="openai/gpt-4o"):
        """
        Send a chat completion request to OpenRouter

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: AI model to use (default: openai/gpt-4o)

        Returns:
            dict: Response from OpenRouter API
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": self.site_url,
            "X-Title": self.site_name,
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": messages
        }

        try:
            response = requests.post(
                url=self.base_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"OpenRouter API error: {str(e)}")

    def extract_response_content(self, response_data):
        """
        Extract the assistant's message from API response

        Args:
            response_data: Response dictionary from OpenRouter

        Returns:
            str: The assistant's message content
        """
        try:
            return response_data['choices'][0]['message']['content']
        except (KeyError, IndexError) as e:
            raise Exception(f"Invalid response format: {str(e)}")
