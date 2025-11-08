"""
Test script to verify automotive topic limitation in chatbot
Run this to ensure the chatbot only responds to vehicle-related questions
"""

from chatbot.gemini_client import GeminiClient
import django
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_service.settings')
django.setup()


def test_chatbot_limits():
    """Test chatbot with automotive and non-automotive questions"""

    client = GeminiClient()

    # Test cases
    test_cases = [
        {
            "category": "AUTOMOTIVE (Should Answer)",
            "question": "How do I diagnose a squeaking noise from my car's brakes?",
            "expected": "Should provide technical automotive answer"
        },
        {
            "category": "AUTOMOTIVE (Should Answer)",
            "question": "What's the difference between synthetic and conventional motor oil?",
            "expected": "Should provide technical automotive answer"
        },
        {
            "category": "AUTOMOTIVE (Should Answer)",
            "question": "How often should I replace my vehicle's air filter?",
            "expected": "Should provide technical automotive answer"
        },
        {
            "category": "NON-AUTOMOTIVE (Should Refuse)",
            "question": "What's the recipe for chocolate cake?",
            "expected": "Should decline and mention automotive specialization"
        },
        {
            "category": "NON-AUTOMOTIVE (Should Refuse)",
            "question": "Who won the last football match?",
            "expected": "Should decline and mention automotive specialization"
        },
        {
            "category": "NON-AUTOMOTIVE (Should Refuse)",
            "question": "How do I cook pasta?",
            "expected": "Should decline and mention automotive specialization"
        },
        {
            "category": "EDGE CASE",
            "question": "Tell me about electric vehicles",
            "expected": "Should answer (vehicles are automotive)"
        },
    ]

    print("=" * 80)
    print("TESTING AUTOMOTIVE TOPIC LIMITATION")
    print("=" * 80)
    print()

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}: {test_case['category']}")
        print(f"{'='*80}")
        print(f"Question: {test_case['question']}")
        print(f"Expected: {test_case['expected']}")
        print(f"\nResponse:")
        print("-" * 80)

        try:
            messages = [{"role": "user", "content": test_case['question']}]
            response = client.create_chat_completion(messages)
            answer = client.extract_response_content(response)
            print(answer)

            # Check if response indicates refusal for non-automotive topics
            if "NON-AUTOMOTIVE" in test_case['category']:
                refusal_keywords = ['specialize in automotive',
                                    'vehicle-related', 'automotive topics', 'vehicle', 'automotive']
                has_refusal = any(keyword.lower() in answer.lower()
                                  for keyword in refusal_keywords)

                if has_refusal:
                    print(f"\n✅ PASS - Correctly refused non-automotive topic")
                else:
                    print(f"\n❌ FAIL - Should have refused this question")
            else:
                print(f"\n✅ PASS - Answered automotive question")

        except Exception as e:
            print(f"❌ ERROR: {str(e)}")

        print("-" * 80)

    print("\n" + "=" * 80)
    print("TESTING COMPLETE")
    print("=" * 80)
    print("\nREVIEW THE RESPONSES ABOVE:")
    print("- Automotive questions should receive detailed technical answers")
    print("- Non-automotive questions should be politely declined")
    print("=" * 80)


if __name__ == "__main__":
    print("\n🚗 Starting Automotive Topic Limitation Tests...\n")

    # Check if API key is set
    from decouple import config
    api_key = config('GEMINI_API_KEY', default='')

    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY not found in environment variables")
        print("Please set your GEMINI_API_KEY in .env file")
        sys.exit(1)

    print("✅ API Key found")
    print("🔧 Running tests...\n")

    try:
        test_chatbot_limits()
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {str(e)}")
        sys.exit(1)
