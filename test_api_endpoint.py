#!/usr/bin/env python3
"""
Test the enhanced /api/diagnose endpoint with medical image
"""

import requests
import json
from PIL import Image, ImageDraw
import io
import tempfile
import os

def create_test_image(disease_type):
    """Create a test medical report image"""
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    test_reports = {
        'thyroid': [
            "THYROID FUNCTION TEST",
            "TSH = 5.2 mIU/L",
            "T3 = 70 ng/dL", 
            "T4 = 4.2 µg/dL",
            "ABNORMAL - Thyroid Disorder"
        ],
        'diabetes': [
            "BLOOD GLUCOSE REPORT",
            "Fasting Glucose = 135 mg/dL",
            "HbA1c = 7.2%",
            "Random Blood Sugar = 245",
            "ABNORMAL - Diabetes"
        ],
        'blood_pressure': [
            "BLOOD PRESSURE REPORT",
            "Systolic = 155 mmHg",
            "Diastolic = 98 mmHg",
            "Heart Rate = 78 bpm",
            "ABNORMAL - Hypertension"
        ]
    }
    
    lines = test_reports.get(disease_type, test_reports['thyroid'])
    
    y = 50
    for line in lines:
        draw.text((50, y), line, fill='black')
        y += 80
    
    return img

def test_api():
    """Test the enhanced API endpoint"""
    
    print("\n" + "="*80)
    print("🧪 TESTING ENHANCED /api/diagnose ENDPOINT")
    print("="*80)
    
    test_cases = [
        ('thyroid', 'generic_file.jpg'),  # Filename doesn't have "thyroid"
        ('diabetes', 'my_test.pdf'),      # Filename doesn't have "diabetes"
        ('blood_pressure', 'report.png')  # Filename doesn't have "bp"
    ]
    
    for disease_type, filename in test_cases:
        print(f"\n{'─'*80}")
        print(f"TEST: {disease_type.upper()} (filename: {filename})")
        print(f"{'─'*80}")
        
        # Create test image
        img = create_test_image(disease_type)
        
        # Prepare request
        url = 'http://localhost:5000/api/diagnose'
        
        # Create form data
        files = {
            'medical_image': (filename, io.BytesIO(
                img.tobytes()
            ), 'image/jpeg')
        }
        data = {
            'patientName': 'Test Patient',
            'age': '30',
            'gender': 'male',
            'contact': '1234567890',
            'symptoms': 'feeling unwell',
            'duration': '1-7 days',
            'severity': 'moderate'
        }
        
        # Save image to file
        temp_dir = tempfile.gettempdir()
        image_path = os.path.join(temp_dir, f'test_{disease_type}.png')
        img.save(image_path)
        
        # Make request
        try:
            with open(image_path, 'rb') as f:
                files['medical_image'] = (filename, f, 'image/png')
                response = requests.post(url, data=data, files={'medical_image': (filename, f, 'image/png')}, timeout=30)
        except Exception as e:
            print(f"❌ Request failed: {e}")
            continue
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Check if diagnosis was successful
            if result.get('success'):
                print("✅ Request successful")
                
                # Check for image diagnosis
                if result.get('symbol_analysis') and result['symbol_analysis'].get('image_diagnosis'):
                    diag = result['symbol_analysis']['image_diagnosis']
                    
                    print(f"\n📊 DIAGNOSIS RESULTS:")
                    print(f"   Disease Detected: {diag.get('disease_detected', 'N/A')}")
                    print(f"   Confidence: {diag.get('confidence', 0):.1%}")
                    print(f"   Detection Method: {diag.get('detection_method', 'N/A')}")
                    
                    # Check for new fields
                    print(f"\n✨ NEW FEATURES:")
                    if diag.get('what_is_present'):
                        print(f"   ✅ What is Present: {len(diag['what_is_present'])} findings")
                        for i, finding in enumerate(diag['what_is_present'][:2], 1):
                            print(f"      {i}. {finding}")
                    else:
                        print(f"   ❌ What is Present: Not available")
                    
                    if diag.get('action_plan'):
                        print(f"   ✅ Action Plan: {len(diag['action_plan'])} steps")
                        for i, step in enumerate(diag['action_plan'][:2], 1):
                            print(f"      {i}. {step[:60]}...")
                    else:
                        print(f"   ❌ Action Plan: Not available")
                    
                    if diag.get('diet_plan'):
                        diet = diag['diet_plan']
                        print(f"   ✅ Diet Plan: Available")
                        if diet.get('foods_to_eat'):
                            print(f"      - Foods to eat: {len(diet['foods_to_eat'])} items")
                        if diet.get('foods_to_avoid'):
                            print(f"      - Foods to avoid: {len(diet['foods_to_avoid'])} items")
                    else:
                        print(f"   ❌ Diet Plan: Not available")
                    
                    if diag.get('recommendations'):
                        meds = diag['recommendations'].get('medications', {})
                        print(f"   ✅ Medications: Available")
                        if meds.get('OTC'):
                            print(f"      - OTC: {len(meds['OTC'])} options")
                        if meds.get('Prescription'):
                            print(f"      - Rx: {len(meds['Prescription'])} options")
                    else:
                        print(f"   ❌ Medications: Not available")
                else:
                    print("❌ No image diagnosis found in response")
                    print(f"   Available keys: {list(result.keys())}")
            else:
                print(f"❌ Request not successful: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ API returned status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    
    print(f"\n{'='*80}")
    print("✅ API TEST COMPLETE")
    print("="*80 + "\n")

if __name__ == '__main__':
    try:
        test_api()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
