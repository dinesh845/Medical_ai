#!/usr/bin/env python3
"""Debug script to check what detect_disease_from_image_content returns"""

import sys
sys.path.insert(0, '/Users/MOHITH/Desktop/medical_ai')

from app import detect_disease_from_image_content, extract_text_from_image
from PIL import Image
import json

# Create a blank image
img = Image.new('RGB', (800, 600), color='white')
img.save('blank_test.jpg')

# Test OCR extraction
print("=" * 60)
print("Testing extract_text_from_image()...")
print("=" * 60)
extracted_text = extract_text_from_image('blank_test.jpg')
print(f"Extracted text length: {len(extracted_text)}")
print(f"Extracted text preview: {extracted_text[:100]}")

# Test disease detection
print("\n" + "=" * 60)
print("Testing detect_disease_from_image_content()...")
print("=" * 60)
result = detect_disease_from_image_content('blank_test.jpg', 'generic_report.jpg')
print(json.dumps(result, indent=2))
