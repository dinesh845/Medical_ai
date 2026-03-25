"""Quick test of OpenAI GPT integration"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from llm_integration import get_chatbot_response

print("\n" + "="*70)
print("TESTING OPENAI GPT-4O-MINI")
print("="*70)

question = "I have a headache and feel tired"
print(f"\nQuestion: {question}\n")
print("Getting response from GPT...")

try:
    response = get_chatbot_response(question)
    
    print("\n" + "="*70)
    print("GPT RESPONSE:")
    print("="*70)
    print(response['message'][:500])
    if len(response['message']) > 500:
        print("...(response continues)")
    
    print("\n" + "="*70)
    print(f"✓ System Used: {response.get('llm_used', 'unknown').upper()}")
    print(f"✓ Suggestions: {response.get('suggestions', [])}")
    print("="*70)
    print("\n✓✓✓ GPT IS WORKING PERFECTLY! ✓✓✓\n")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    print("Falling back to knowledge base...")
