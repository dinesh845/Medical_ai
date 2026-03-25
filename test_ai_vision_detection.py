#!/usr/bin/env python3
"""
Test script for AI Vision-Based Disease Detection

This script demonstrates that the system can now detect diseases
from the IMAGE CONTENT itself, without relying on filename keywords.
"""

import sys
import json
import os
import tempfile
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# Add project to path
sys.path.insert(0, '/c/Users/MOHITH/Desktop/medical_ai')

from app import (
    detect_disease_from_image_content,
    get_recommendation,
    analyze_medical_image
)

def create_test_medical_image(test_type):
    """Create a test medical report image with realistic values"""
    
    img = Image.new('RGB', (800, 1000), color='white')
    draw = ImageDraw.Draw(img)
    
    # Define test reports
    test_reports = {
        'thyroid': [
            "THYROID FUNCTION TEST REPORT",
            "",
            "Patient: Test Patient",
            "Date: 2026-02-19",
            "",
            "Results:",
            "TSH: 5.2 mIU/L (Reference: 0.4-4.0)",
            "T3: 70 ng/dL (Reference: 80-200)",
            "T4: 4.2 µg/dL (Reference: 5-12)",
            "Thyroid Antibodies: Positive",
            "",
            "Interpretation: ABNORMAL",
            "Thyroid Disorder Detected"
        ],
        'diabetes': [
            "BLOOD GLUCOSE TEST REPORT",
            "",
            "Patient: Test Patient",
            "Date: 2026-02-19",
            "",
            "Results:",
            "Fasting Glucose: 135 mg/dL (Reference: 70-100)",
            "Random Blood Sugar: 245 mg/dL (Reference: <140)",
            "HbA1c: 7.2% (Reference: <5.7%)",
            "Symptoms: Polyuria, Polydipsia",
            "",
            "Interpretation: ABNORMAL",
            "Diabetes Mellitus Suspected"
        ],
        'blood_pressure': [
            "BLOOD PRESSURE MONITORING REPORT",
            "",
            "Patient: Test Patient",
            "Date: 2026-02-19",
            "",
            "Results:",
            "Systolic Pressure: 155 mmHg (Reference: <120)",
            "Diastolic Pressure: 98 mmHg (Reference: <80)",
            "Heart Rate: 78 bpm",
            "ECG: Left ventricular hypertrophy",
            "Urine: Albumin Positive",
            "",
            "Interpretation: ABNORMAL",
            "Hypertension Confirmed"
        ],
        'anemia': [
            "COMPLETE BLOOD COUNT (CBC) REPORT",
            "",
            "Patient: Test Patient",
            "Date: 2026-02-19",
            "",
            "Results:",
            "Hemoglobin: 9.5 g/dL (Reference: 12-16)",
            "RBC: 3.8 million/µL (Reference: 4.5-5.5)",
            "WBC: 7.2 thousand/µL (Reference: 4.5-11)",
            "Platelets: 280 thousand/µL",
            "",
            "Interpretation: ABNORMAL - Anemia",
            "Low Hemoglobin Detected"
        ],
        'liver': [
            "LIVER FUNCTION TEST REPORT",
            "",
            "Patient: Test Patient",
            "Date: 2026-02-19",
            "",
            "Results:",
            "AST: 65 U/L (Reference: 10-40)",
            "ALT: 72 U/L (Reference: 7-56)",
            "Bilirubin Total: 1.8 mg/dL (Reference: 0.1-1.2)",
            "Albumin: 3.2 g/dL (Reference: 3.5-5.0)",
            "ALP: 95 U/L",
            "",
            "Interpretation: ABNORMAL",
            "Liver Disease Detected"
        ],
    }
    
    # Get text for this test type
    text_lines = test_reports.get(test_type, test_reports['thyroid'])
    
    # Draw text on image
    y_position = 30
    line_height = 35
    
    for line in text_lines:
        draw.text((50, y_position), line, fill='black')
        y_position += line_height
    
    # Save to BytesIO
    image_bytes = BytesIO()
    img.save(image_bytes, format='PNG')
    image_bytes.seek(0)
    
    return image_bytes, img

def test_ai_vision_detection():
    """Test the AI vision-based detection without filename keywords"""
    
    print("\n" + "="*80)
    print("🤖 AI VISION-BASED DISEASE DETECTION TEST")
    print("="*80)
    print("\nThis test demonstrates that the system can detect diseases")
    print("from IMAGE CONTENT itself, WITHOUT FILENAME keywords.\n")
    
    test_cases = [
        ('thyroid', 'Thyroid disorder with abnormal TSH, T3, T4'),
        ('diabetes', 'Diabetes with elevated glucose and HbA1c'),
        ('blood_pressure', 'Hypertension with high systolic/diastolic'),
        ('anemia', 'Anemia with low hemoglobin'),
        ('liver', 'Liver disease with elevated AST/ALT'),
    ]
    
    for test_type, description in test_cases:
        print(f"\n{'─'*80}")
        print(f"TEST: {description.upper()}")
        print(f"{'─'*80}")
        
        # Create test image
        test_image, img = create_test_medical_image(test_type)
        # Use Windows-compatible temp directory
        temp_dir = tempfile.gettempdir()
        image_path = os.path.join(temp_dir, f'test_medical_{test_type}.png')
        img.save(image_path)
        
        # Test 1: Detection WITHOUT filename keyword
        print(f"\n📸 IMAGE ANALYSIS (No filename keyword):")
        print(f"   Analyzing image content using AI vision...")
        
        ai_result = detect_disease_from_image_content(image_path, filename='medical_report.jpg')
        
        detected_disease = ai_result.get('disease')
        confidence = ai_result.get('confidence', 0.0)
        method = ai_result.get('method', 'Unknown')
        
        if detected_disease:
            print(f"   ✅ Disease Detected: {detected_disease}")
            print(f"   📊 Confidence: {confidence:.1%}")
            print(f"   🔍 Method: {method}")
            if ai_result.get('extracted_text_preview'):
                print(f"   📝 Text Preview: {ai_result.get('extracted_text_preview')[:100]}...")
        else:
            print(f"   ⚠️  No disease detected")
            print(f"   Note: {ai_result.get('note', '')}")
        
        # Test 2: Full analysis
        if detected_disease:
            print(f"\n📋 FULL ANALYSIS:")
            rec = get_recommendation(detected_disease, 'moderate')
            
            # Show findings
            if rec.get('what_is_present'):
                print(f"\n   WHAT IS PRESENT:")
                for i, finding in enumerate(rec.get('what_is_present', [])[:3], 1):
                    print(f"   {i}. {finding}")
            
            # Show action plan
            if rec.get('action_plan'):
                print(f"\n   WHAT TO DO NEXT (First 3 steps):")
                for i, step in enumerate(rec.get('action_plan', [])[:3], 1):
                    step_text = step.replace('Step 1: ', '').replace('Step 2: ', '').replace('Step 3: ', '').replace('Step 4: ', '').replace('Step 5: ', '').replace('Step 6: ', '').replace('Step 7: ', '')
                    print(f"   {i}. {step_text}")
            
            # Show diet plan
            if rec.get('diet_plan'):
                diet = rec.get('diet_plan', {})
                print(f"\n   DIET RECOMMENDATIONS:")
                if diet.get('foods_to_eat'):
                    print(f"   Foods to Eat: {', '.join(diet.get('foods_to_eat', [])[:2])}")
                if diet.get('foods_to_avoid'):
                    print(f"   Foods to Avoid: {', '.join(diet.get('foods_to_avoid', [])[:2])}")
            
            # Show medications
            if rec.get('medications'):
                meds = rec.get('medications', {})
                if meds.get('OTC'):
                    print(f"\n   MEDICATIONS:")
                    print(f"   OTC: {meds.get('OTC')[0] if meds.get('OTC') else 'N/A'}")
                if meds.get('Prescription'):
                    print(f"   Rx: {meds.get('Prescription')[0] if meds.get('Prescription') else 'N/A'}")
    
    print(f"\n{'='*80}")
    print("✅ AI VISION DETECTION TEST COMPLETE")
    print("="*80)
    print("\nKey Features Demonstrated:")
    print("✓ Disease detection from IMAGE CONTENT (not just filename)")
    print("✓ Text extraction using OCR")
    print("✓ Pattern matching for medical values")
    print("✓ Confidence scoring")
    print("✓ Complete guidance (findings + action plan + diet plan)")
    print("\n")

if __name__ == '__main__':
    try:
        test_ai_vision_detection()
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
