#!/usr/bin/env python3
"""Debug script to see actual API response structure"""

import requests
import json
from PIL import Image

# Create test image
img = Image.new('RGB', (800, 600), color='white')
img.save("debug_test.jpg")

# Make API request
try:
    with open("debug_test.jpg", 'rb') as f:
        files = {'medical_image': f}
        response = requests.post("http://localhost:5000/api/diagnose", files=files, timeout=10)
    
    print("Status:", response.status_code)
    print("\nRaw Response:")
    print(json.dumps(response.json(), indent=2))
    
except Exception as e:
    print(f"Error: {e}")
