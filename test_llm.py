"""Test LLM Integration"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from llm_integration import medical_llm_chat, OPENAI_AVAILABLE

print("=" * 70)
print("LLM INTEGRATION TEST")
print("=" * 70)

print(f"\n✓ OpenAI Available: {OPENAI_AVAILABLE}")
print(f"✓ Using: {'OpenAI GPT' if OPENAI_AVAILABLE else 'Medical Knowledge Base (Free)'}")

if not OPENAI_AVAILABLE:
    print("\n💡 TIP: To use OpenAI GPT for better responses:")
    print("   1. Create .env file")
    print("   2. Add: OPENAI_API_KEY=sk-your-key-here")
    print("   3. Get key from: https://platform.openai.com/api-keys")
    print("\n   The chatbot works perfectly without it too!")

print("\n" + "=" * 70)
print("TESTING CHATBOT")
print("=" * 70)

test_messages = [
    "Hello",
    "I have a fever and headache",
    "How do I know if it's serious?",
]

for msg in test_messages:
    print(f"\n{'─' * 70}")
    print(f"USER: {msg}")
    print(f"{'─' * 70}")
    
    try:
        response = medical_llm_chat.get_response(msg)
        print(f"\nBOT: {response['message'][:300]}...")
        print(f"\nSuggestions: {response.get('suggestions', [])}")
        print(f"Using: {response.get('llm_used', 'unknown')}")
    except Exception as e:
        print(f"\n✗ ERROR: {e}")

print("\n" + "=" * 70)
print("✓ TEST COMPLETE")
print("=" * 70)
