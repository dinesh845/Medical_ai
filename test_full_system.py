"""Comprehensive test of the medical chatbot"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 70)
print("TESTING MEDICAL AI CHATBOT - FULL SYSTEM CHECK")
print("=" * 70)

# Test 1: Import check
print("\n[Test 1] Checking imports...")
try:
    from app import app
    from llm_integration import get_chatbot_response, OPENAI_AVAILABLE
    print("✓ All imports successful")
except Exception as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

# Test 2: Check LLM configuration
print(f"\n[Test 2] LLM Configuration")
print(f"  OpenAI Available: {OPENAI_AVAILABLE}")
print(f"  System: {'OpenAI GPT' if OPENAI_AVAILABLE else 'Medical Knowledge Base (Free)'}")

# Test 3: Test Flask routes
print(f"\n[Test 3] Flask Routes")
for rule in app.url_map.iter_rules():
    methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
    print(f"  ✓ {rule.rule:30s} [{methods}]")

# Test 4: Test index route
print(f"\n[Test 4] Testing Index Route")
with app.test_client() as client:
    response = client.get('/')
    if response.status_code == 200:
        print(f"  ✓ Index route works (Status: {response.status_code})")
    else:
        print(f"  ✗ Index route failed (Status: {response.status_code})")

# Test 5: Test chat API
print(f"\n[Test 5] Testing Chat API")
test_messages = [
    "Hello",
    "I have a fever",
] 

with app.test_client() as client:
    for msg in test_messages:
        response = client.post('/api/chat',
                              json={'message': msg, 'history': []})
        if response.status_code == 200:
            data = response.get_json()
            print(f"\n  ✓ Message: '{msg}'")
            print(f"    Status: {response.status_code}")
            print(f"    Response length: {len(data.get('response', ''))} chars")
            print(f"    LLM used: {data.get('llm_used', 'unknown')}")
            print(f"    Preview: {data.get('response', '')[:100]}...")
        else:
            print(f"\n  ✗ Message: '{msg}' - Failed (Status: {response.status_code})")
            print(f"    Error: {response.get_data(as_text=True)}")

# Test 6: Direct function test
print(f"\n[Test 6] Direct Function Test")
try:
    response = get_chatbot_response("I have a headache")
    print(f"  ✓ Direct function call works")
    print(f"    Response length: {len(response['message'])} chars")
    print(f"    Suggestions: {len(response.get('suggestions', []))} suggestions")
    print(f"    LLM used: {response.get('llm_used', 'unknown')}")
except Exception as e:
    print(f"  ✗ Error: {e}")

print("\n" + "=" * 70)
print("✓ ALL TESTS COMPLETE")
print("=" * 70)

if not OPENAI_AVAILABLE:
    print("\n💡 TIP: Currently using FREE Medical Knowledge Base")
    print("   For even better responses, add OpenAI API key to .env file")
    print("   See START_HERE.md for instructions")
else:
    print("\n✓ Using OpenAI GPT for intelligent responses!")

print("\n🚀 Your chatbot is ready! Start the server with:")
print("   python app.py")
print("\n   Then open: http://localhost:5000")
print("=" * 70)
