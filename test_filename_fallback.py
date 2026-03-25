#!/usr/bin/env python3
"""
Quick test to verify the API returns complete data with proper filename
"""

import requests
import json
from PIL import Image, ImageDraw
import io
import tempfile
import os

def create_test_image():
    """Create a simple test image"""
    img = Image.new('RGB', (400, 300), color='white')
    draw = ImageDraw.Draw(img)
    draw.text((50, 50), "MEDICAL REPORT", fill='black')
    return img

def test_with_filename():
    """Test the API with proper disease keyword in filename"""
    
    print("\n" + "="*80)
    print("🧪 TESTING WITH PROPER FILENAMES (Fallback Mechanism)")
    print("="*80 + "\n")
    
    test_cases = [
        ('thyroid_report.jpg', 'Thyroid Disorder'),
        ('diabetes_test.jpg', 'Diabetes Mellitus'),
        ('blood_pressure_check.jpg', 'Hypertension (High Blood Pressure)')
    ]
    
    for filename, expected_disease in test_cases:
        print(f"Testing: {filename}")
        print(f"Expected: {expected_disease}")
        
        img = create_test_image()
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, filename)
        img.save(temp_file)
        
        url = 'http://localhost:5000/api/diagnose'
        
        try:
            with open(temp_file, 'rb') as f:
                response = requests.post(url, 
                    data={
                        'patientName': 'Test',
                        'age': '30',
                        'gender': 'male',
                        'contact': '1234567890',
                        'symptoms': 'test',
                        'duration': '1-7 days',
                        'severity': 'moderate'
                    },
                    files={'medical_image': (filename, f, 'image/jpeg')},
                    timeout=30
                )
            
            if response.status_code == 200:
                result = response.json()
                diag = result.get('symbol_analysis', {}).get('image_diagnosis', {})
                
                detected = diag.get('disease_detected', 'Not detected')
                print(f"✅ Detected: {detected}")
                
                # Check for all new fields
                has_findings = bool(diag.get('what_is_present'))
                has_plan = bool(diag.get('action_plan'))
                has_diet = bool(diag.get('diet_plan'))
                has_meds = bool(diag.get('recommendations'))
                
                print(f"   └─ ✅ Findings: {'Yes' if has_findings else 'No'}")
                print(f"   └─ ✅ Action Plan: {'Yes' if has_plan else 'No'}")
                print(f"   └─ ✅ Diet Plan: {'Yes' if has_diet else 'No'}")
                print(f"   └─ ✅ Medications: {'Yes' if has_meds else 'No'}")
            else:
                print(f"❌ Error: {response.status_code}")
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print()

if __name__ == '__main__':
    test_with_filename()
