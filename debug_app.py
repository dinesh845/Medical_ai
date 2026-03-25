"""Debug script to test Flask app routes"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from app import app

print("=" * 60)
print("Flask App Debug Information")
print("=" * 60)

print(f"\nApp name: {app.name}")
print(f"Debug mode: {app.debug}")

print("\nRegistered Routes:")
print("-" * 60)
for rule in app.url_map.iter_rules():
    methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
    print(f"{rule.rule:30s} [{methods}]")

print("\n" + "=" * 60)
print("Testing index route...")
print("=" * 60)

with app.test_client() as client:
    try:
        response = client.get('/')
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response.content_type}")
        print(f"Content Length: {len(response.data)} bytes")
        if response.status_code == 200:
            print("✓ SUCCESS: Index route is working!")
        else:
            print(f"✗ ERROR: Got status {response.status_code}")
            print(f"Response: {response.data[:200]}")
    except Exception as e:
        print(f"✗ ERROR: {e}")

print("\n" + "=" * 60)
