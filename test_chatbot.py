"""Test the enhanced medical chatbot"""

import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from medical_knowledge import medical_kb

# Test various queries
test_queries = [
    "Hello",
    "I have a fever",
    "I have a severe headache",
    "I'm experiencing chest pain",
    "I feel anxious",
    "I have a cough",
    "My stomach hurts",
    "I'm having difficulty breathing"
]

print("=" * 70)
print("TESTING ENHANCED MEDICAL CHATBOT")
print("=" * 70)

for query in test_queries:
    print(f"\n{'='*70}")
    print(f"USER: {query}")
    print(f"{'='*70}")
    
    response = medical_kb.get_response(query)
    print(f"\nBOT RESPONSE:\n{response['message']}")
    print(f"\nSUGGESTIONS: {response.get('suggestions', [])}")
    print()

print("\n" + "=" * 70)
print("TEST COMPLETED")
print("=" * 70)
