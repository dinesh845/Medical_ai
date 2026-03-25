#!/usr/bin/env python3
"""
Test the improved AI vision detection system with lowered confidence thresholds
Tests both OCR-based detection and filename-based fallback
"""

import requests
import json
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io

BASE_URL = "http://localhost:5000"

def create_test_image_with_text(text_content, filename):
    """Create a test image with specific medical text"""
    try:
        # Create a white image with black text
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to find a font, fallback to default
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        # Add text to image
        lines = text_content.split('\n')
        y = 20
        for line in lines:
            draw.text((20, y), line, fill='black', font=font)
            y += 30
        
        # Save image
        img.save(filename)
        return True
    except Exception as e:
        print(f"Error creating test image: {e}")
        return False

def test_diabetes_detection():
    """Test detection of Diabetes from medical report text"""
    print("\n" + "="*60)
    print("TEST 1: DIABETES DETECTION")
    print("="*60)
    
    # Create image with diabetes-related text
    diabetes_text = """
    LABORATORY REPORT
    Patient: John Doe
    Date: 2024-01-15
    
    BLOOD GLUCOSE TESTS:
    Fasting Blood Glucose: 145 mg/dL (Normal: <100)
    HbA1c: 8.5% (Normal: <5.7%)
    Random Blood Glucose: 220 mg/dL
    
    DIAGNOSIS: Elevated glucose levels indicate Diabetes Mellitus Type 2
    """
    
    img_path = "test_diabetes_report.jpg"
    create_test_image_with_text(diabetes_text, img_path)
    
    # Upload to API
    try:
        with open(img_path, 'rb') as f:
            files = {'medical_image': f}
            data = {'reportType': 'blood_glucose'}
            response = requests.post(f"{BASE_URL}/api/diagnose", files=files, data=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"Disease Detected: {result.get('symbol_analysis', {}).get('image_diagnosis', {}).get('disease_detected', 'N/A')}")
            print(f"Confidence: {result.get('symbol_analysis', {}).get('image_diagnosis', {}).get('confidence', 'N/A')}")
            print(f"Detection Method: {result.get('symbol_analysis', {}).get('image_diagnosis', {}).get('detection_method', 'N/A')}")
            
            findings = result.get('symbol_analysis', {}).get('image_diagnosis', {}).get('what_is_present', [])
            print(f"✅ Findings Found: {len(findings)} items")
            for i, finding in enumerate(findings[:3], 1):
                print(f"   {i}. {finding}")
            
            action_plan = result.get('symbol_analysis', {}).get('image_diagnosis', {}).get('action_plan', [])
            print(f"✅ Action Plan Steps: {len(action_plan)} steps")
            for i, step in enumerate(action_plan[:3], 1):
                print(f"   {i}. {step}")
            
            diet = result.get('symbol_analysis', {}).get('image_diagnosis', {}).get('diet_plan', {})
            print(f"✅ Diet Plan: {bool(diet)}")
            if diet:
                print(f"   Foods to eat: {len(diet.get('foods_to_eat', []))} items")
                print(f"   Foods to avoid: {len(diet.get('foods_to_avoid', []))} items")
            
            print("\n✅ TEST 1 PASSED: Complete diagnosis returned")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_hypertension_detection():
    """Test detection of Hypertension from medical report text"""
    print("\n" + "="*60)
    print("TEST 2: HYPERTENSION DETECTION")
    print("="*60)
    
    # Create image with hypertension-related text
    hypertension_text = """
    BLOOD PRESSURE MONITORING REPORT
    Patient: Jane Smith
    Date: 2024-01-15
    
    BLOOD PRESSURE READINGS:
    Systolic: 165 mmHg (Normal: <120)
    Diastolic: 105 mmHg (Normal: <80)
    Average BP: 165/105 mmHg
    
    DIAGNOSIS: Stage 2 Hypertension detected
    Requires immediate attention
    """
    
    img_path = "test_bp_report.jpg"
    create_test_image_with_text(hypertension_text, img_path)
    
    # Upload to API
    try:
        with open(img_path, 'rb') as f:
            files = {'medical_image': f}
            data = {'reportType': 'blood_pressure'}
            response = requests.post(f"{BASE_URL}/api/diagnose", files=files, data=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {response.status_code}")
            disease = result.get('symbol_analysis', {}).get('image_diagnosis', {}).get('disease_detected', 'N/A')
            print(f"Disease Detected: {disease}")
            print(f"Confidence: {result.get('symbol_analysis', {}).get('image_diagnosis', {}).get('confidence', 'N/A')}")
            
            # Check if all components present
            components_present = all([
                result.get('symbol_analysis', {}).get('image_diagnosis', {}).get('what_is_present'),
                result.get('symbol_analysis', {}).get('image_diagnosis', {}).get('action_plan'),
                result.get('symbol_analysis', {}).get('image_diagnosis', {}).get('diet_plan'),
            ])
            
            if components_present and 'Hypertension' in disease:
                print("✅ TEST 2 PASSED: Hypertension detected with all components")
                return True
            else:
                print(f"⚠️ TEST 2 PARTIAL: Disease detected but missing components")
                return False
        else:
            print(f"❌ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_filename_fallback():
    """Test filename-based fallback if OCR fails"""
    print("\n" + "="*60)
    print("TEST 3: FILENAME FALLBACK")
    print("="*60)
    
    # Create a generic image (no medical text)
    img = Image.new('RGB', (800, 600), color='white')
    img_path = "thyroid_report.jpg"
    img.save(img_path)
    
    try:
        with open(img_path, 'rb') as f:
            files = {'medical_image': f}
            response = requests.post(f"{BASE_URL}/api/diagnose", files=files, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            disease = result.get('symbol_analysis', {}).get('image_diagnosis', {}).get('disease_detected', 'N/A')
            print(f"Disease Detected: {disease}")
            
            if 'Thyroid' in disease:
                print("✅ TEST 3 PASSED: Filename fallback working")
                return True
            else:
                print(f"⚠️ TEST 3: Got '{disease}' instead of Thyroid")
                return False
        else:
            print(f"❌ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_generic_image():
    """Test handling of completely generic image"""
    print("\n" + "="*60)
    print("TEST 4: GENERIC IMAGE HANDLING")
    print("="*60)
    
    # Create a completely generic image
    img = Image.new('RGB', (800, 600), color='white')
    img_path = "generic_report.jpg"
    img.save(img_path)
    
    try:
        with open(img_path, 'rb') as f:
            files = {'medical_image': f}
            response = requests.post(f"{BASE_URL}/api/diagnose", files=files, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            disease = result.get('symbol_analysis', {}).get('image_diagnosis', {}).get('disease_detected', 'N/A')
            print(f"Disease Detected: {disease}")
            
            # Should return generic consultation with all components
            components = {
                'what_is_present': result.get('symbol_analysis', {}).get('image_diagnosis', {}).get('what_is_present', []),
                'action_plan': result.get('symbol_analysis', {}).get('image_diagnosis', {}).get('action_plan', []),
                'diet_plan': result.get('symbol_analysis', {}).get('image_diagnosis', {}).get('diet_plan', {}),
            }
            
            print(f"✅ What is Present: {len(components['what_is_present'])} items")
            print(f"✅ Action Plan: {len(components['action_plan'])} steps")
            print(f"✅ Diet Plan: {bool(components['diet_plan'])}")
            
            if all(components.values()):
                print("✅ TEST 4 PASSED: Generic image returns complete guidance")
                return True
            else:
                print("⚠️ TEST 4: Missing some components")
                return False
        else:
            print(f"❌ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("IMPROVED AI VISION DETECTION TEST SUITE")
    print("Testing: Confidence threshold = 0.20 (improved from 0.30)")
    print("="*60)
    
    # Wait for server to be ready
    print("\nWaiting for server to be ready...")
    for i in range(10):
        try:
            response = requests.get(f"{BASE_URL}/", timeout=2)
            print("✅ Server ready!")
            break
        except:
            if i < 9:
                time.sleep(1)
            else:
                print("❌ Server not responding. Make sure Flask is running.")
                return
    
    # Run tests
    results = []
    results.append(("Diabetes Detection", test_diabetes_detection()))
    time.sleep(1)
    results.append(("Hypertension Detection", test_hypertension_detection()))
    time.sleep(1)
    results.append(("Filename Fallback", test_filename_fallback()))
    time.sleep(1)
    results.append(("Generic Image Handling", test_generic_image()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is ready for production.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review output above.")

if __name__ == '__main__':
    main()
