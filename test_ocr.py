#!/usr/bin/env python3
"""Test OCR extraction directly"""

import sys
sys.path.insert(0, r'c:\Users\MOHITH\Desktop\medical_ai')

from PIL import Image, ImageDraw, ImageFont
import os
from app import extract_text_from_image

# Create a test image with medical text
img = Image.new('RGB', (1000, 600), color='white')
draw = ImageDraw.Draw(img)

try:
    font = ImageFont.truetype("arial.ttf", 24)
except:
    font = ImageFont.load_default()

medical_text = "Blood Glucose: 145 mg/dL\nHbA1c: 8.5%\nDiabetes Mellitus Diagnosis"

lines = medical_text.split('\n')
y = 50
for line in lines:
    draw.text((20, y), line, fill='black', font=font)
    y += 60

img.save('ocr_test.jpg')

print("Testing OCR extraction...")
print("=" * 60)

extracted = extract_text_from_image('ocr_test.jpg')
print(f"Extracted text length: {len(extracted)}")
print(f"Extracted text:\n{extracted}")

os.remove('ocr_test.jpg')
