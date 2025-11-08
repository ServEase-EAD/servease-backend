import requests
import json
from decouple import config


class GeminiClient:
    """Client for interacting with Google Gemini API directly"""

    # System instruction to limit chatbot to automotive/vehicle industry topics
    AUTOMOTIVE_SYSTEM_INSTRUCTION = """You are an expert Automotive Industry AI Assistant specialized in vehicle-related topics.

YOUR EXPERTISE COVERS:
- Vehicle repairs, maintenance, and diagnostics (all vehicle types: cars, trucks, motorcycles, boats, etc.)
- Vehicle modifications, customization, and upgrades
- Automotive parts, components, and equipment
- Engine systems, transmissions, brakes, suspension, electrical systems
- Vehicle troubleshooting and problem diagnosis
- Automotive industry standards and best practices
- Vehicle specifications, models, and comparisons
- Automotive tools and workshop equipment
- Vehicle safety and inspection procedures
- Fuel systems, emissions, and environmental considerations

YOU MUST STRICTLY REFUSE:
- Non-automotive topics (cooking, sports, politics, entertainment, weather, etc.)
- Company-specific information (you don't have access to ServEase internal data)
- Medical, legal, or financial advice
- Personal opinions on controversial topics
- Any topic unrelated to vehicles or the automotive industry

RESPONSE GUIDELINES:
1. For automotive questions: Provide detailed, accurate, and helpful technical information
2. For off-topic questions: Politely respond with: "I specialize in automotive and vehicle-related topics only. How can I help you with your vehicle or automotive service needs?"
3. Be professional, clear, and technically accurate
4. Use proper automotive terminology
5. Stay focused on the vehicle industry context

Remember: You are an automotive expert, not a general assistant. Stay in your lane!"""

    def __init__(self):
        self.api_key = config('GEMINI_API_KEY', default='')
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.model = "gemini-2.5-flash"  # Free model

    def create_chat_completion(self, messages, model=None):
        """
        Send a chat completion request to Google Gemini API

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: AI model to use (default: gemini-2.5-flash)

        Returns:
            dict: Response formatted in a standard shape for compatibility with the views
        """
        if model is None:
            model = self.model

        # Convert incoming message list to Gemini request format
        gemini_contents = self._convert_messages_to_gemini_format(messages)

        url = f"{self.base_url}/{model}:generateContent?key={self.api_key}"

        payload = {
            "contents": gemini_contents,
            "systemInstruction": {
                "parts": [{"text": self.AUTOMOTIVE_SYSTEM_INSTRUCTION}]
            }
        }

        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                url=url,
                headers=headers,
                data=json.dumps(payload),
                timeout=30
            )

            # If error, try to get detailed error message
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    error_message = error_data.get('error', {}).get(
                        'message', str(response.text))
                    raise Exception(
                        f"Gemini API error ({response.status_code}): {error_message}")
                except json.JSONDecodeError:
                    response.raise_for_status()

            response.raise_for_status()
            gemini_response = response.json()

            # Convert Gemini response to standard format
            return self._convert_gemini_response_to_standard(gemini_response)

        except requests.exceptions.RequestException as e:
            raise Exception(f"Gemini API error: {str(e)}")

    def _convert_messages_to_gemini_format(self, messages):
        """
        Convert generic message list to Gemini format

        Incoming format: [{"role": "user", "content": "text"}]
        Gemini format: [{"role": "user", "parts": [{"text": "text"}]}]
        """
        gemini_contents = []

        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')

            # Map role names
            if role == 'assistant':
                role = 'model'  # Gemini uses 'model' instead of 'assistant'
            elif role == 'system':
                # Gemini doesn't have system role, convert to user message
                role = 'user'

            gemini_contents.append({
                "role": role,
                "parts": [{"text": content}]
            })

        return gemini_contents

    def _convert_gemini_response_to_standard(self, gemini_response):
        """
        Convert Gemini response format to a standard format used by the views

        Returns standard format: {"choices": [{"message": {"content": "..."}}]}
        """
        try:
            text = gemini_response['candidates'][0]['content']['parts'][0]['text']

            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": text
                        }
                    }
                ]
            }
        except (KeyError, IndexError) as e:
            raise Exception(f"Invalid Gemini response format: {str(e)}")

    def extract_response_content(self, response_data):
        """
        Extract the assistant's message from API response

        Args:
            response_data: Response dictionary (already in standard format)

        Returns:
            str: The assistant's message content
        """
        try:
            return response_data['choices'][0]['message']['content']
        except (KeyError, IndexError) as e:
            raise Exception(f"Invalid response format: {str(e)}")

    def check_quota(self):
        """
        Note: Google Gemini API doesn't have a direct quota check endpoint
        Returns a placeholder response
        """
        return {
            "message": "Gemini API uses quota system. Check Google Cloud Console for usage.",
            "free_tier_limits": {
                "requests_per_minute": 15,
                "tokens_per_minute": 1000000,
                "requests_per_day": 1500
            }
        }
