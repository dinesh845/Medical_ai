#!/usr/bin/env python3
"""
Advanced test: Simulate medical reports with text and verify AI vision detection works
This tests the OCR + Pattern Matching detection without relying on filename keywords
"""

import requests
import json
import time
from PIL import Image, ImageDraw, ImageFont
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_URL = "http://localhost:5000"

def create_medical_report_image(disease_type, filename):
    """Create a realistic medical report image with proper medical text"""
    
    medical_reports = {
        'diabetes': """
HOSPITAL LAB REPORT
Patient: John Doe | Age: 45 | Date: 2024-01-15

BLOOD GLUCOSE TEST RESULTS
=========================================
Fasting Blood Glucose: 145 mg/dL [Normal <100]
Post Meal Glucose: 220 mg/dL [Normal <140]
HbA1c: 8.5% [Normal <5.7%]
Random Blood Glucose: 198 mg/dL

INTERPRETATION:
Elevated glucose levels indicate Type 2 Diabetes Mellitus.
Patient requires insulin therapy and lifestyle modification.

RECOMMENDATIONS:
- Metformin 500mg BID
- Dietary modification
- Exercise 30 min daily
        """,
        
        'hypertension': """
CARDIOLOGY REPORT
Patient: Jane Smith | Date: 2024-01-15

BLOOD PRESSURE MONITORING
=========================================
Systolic BP: 165 mmHg [Normal <120]
Diastolic BP: 105 mmHg [Normal <80]
Mean Arterial Pressure: 125 mmHg [Normal <93]
Heart Rate: 92 bpm [Normal 60-100]

DIAGNOSIS: Stage 2 Hypertension (Essential)
Left Ventricular Hypertrophy (LVH) present

TREATMENT PLAN:
- Lisinopril 10mg OD
- Amlodipine 5mg OD
- Regular BP monitoring
- Sodium restriction diet
        """,
        
        'thyroid': """
ENDOCRINOLOGY REPORTS
Patient: Michael Johnson | Date: 2024-01-14

THYROID FUNCTION TESTS
=========================================
TSH Level: 8.5 mIU/L [Normal 0.4-4.0]
Free T4: 5.2 pmol/L [Normal 9-19]
Free T3: 2.1 pmol/L [Normal 2.6-5.7]
Total Thyroid Antibodies: Elevated

DIAGNOSIS: Primary Hypothyroidism
Likely autoimmune (Hashimoto's thyroiditis)

MANAGEMENT:
- Levothyroxine 50mcg OD
- Repeat TSH in 6-8 weeks
- Monitor symptoms
        """,
        
        'kidney': """
NEPHROLOGY/RENAL FUNCTION REPORT
Patient: Robert Williams | Date: 2024-01-13

KIDNEY FUNCTION TESTS
=========================================
Serum Creatinine: 2.1 mg/dL [Normal 0.7-1.3]
BUN (Blood Urea Nitrogen): 45 mg/dL [Normal 7-20]
eGFR (Estimated GFR): 28 mL/min [Normal >60]
Serum Albumin: 2.8 g/dL [Normal 3.5-5.0]
Urine Protein: 4.2 g/24h [Normal <0.15]

DIAGNOSIS: Chronic Kidney Disease, Stage 3b
Proteinuria present - significant renal dysfunction

RECOMMENDATIONS:
- ACE inhibitor therapy
- Nephrology consultation
- Dietary protein restriction
        """
    }
    
    text = medical_reports.get(disease_type, medical_reports['diabetes'])
    
    try:
        # Create image with medical text
        img = Image.new('RGB', (1000, 1400), color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to use a reasonable font size
        try:
            font = ImageFont.truetype("arial.ttf", 18)
            title_font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
            title_font = font
        
        # Draw medical text
        lines = text.strip().split('\n')
        y = 20
        
        for line in lines:
            if line.strip().isupper() and len(line) < 40:
                draw.text((20, y), line.strip(), fill='black', font=title_font)
            else:
                draw.text((20, y), line, fill='black', font=font)
            y += 25
        
        # Save image
        img.save(filename)
        print(f"Created {disease_type} image: {filename}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_ai_vision_detection(disease_type):
    """Test AI vision (OCR) detection without filename keywords"""
    print("\n" + "="*60)
    print(f"TESTING: {disease_type.upper()} - AI VISION DETECTION")
    print("="*60)
    
    # Create image with medical report text
    img_filename = f"ocr_test_{disease_type}.jpg"
    generic_filename = "medical_report.jpg"  # No disease keywords in filename!
    
    if not create_medical_report_image(disease_type, img_filename):
        print("❌ Failed to create test image")
        return False
    
    # Copy to generic filename (so AI must detect from content, not filename)
    import shutil
    shutil.copy(img_filename, generic_filename)
    
    try:
        with open(generic_filename, 'rb') as f:
            files = {'medical_image': f}
            response = requests.post(f"{BASE_URL}/api/diagnose", files=files, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            diagnosis = result.get('symbol_analysis', {}).get('image_diagnosis', {})
            
            disease_detected = diagnosis.get('disease_detected', 'N/A')
            confidence = diagnosis.get('confidence', 0)
            method = diagnosis.get('detection_method', 'N/A')
            
            print(f"\n📋 Disease Detected: {disease_detected}")
            print(f"📊 Confidence: {confidence} ({int(confidence*100)}%)")
            print(f"🔍 Detection Method: {method}")
            
            # Check components
            findings = diagnosis.get('what_is_present', [])
            actions = diagnosis.get('action_plan', [])
            diet = diagnosis.get('diet_plan', {})
            
            print(f"\n✅ Findings: {len(findings)} items")
            for i, finding in enumerate(findings[:3], 1):
                print(f"   {i}. {finding}")
            
            print(f"✅ Action Plan: {len(actions)} steps")
            for i, action in enumerate(actions[:3], 1):
                print(f"   {i}. {action}")
            
            if diet:
                print(f"✅ Diet Plan: {len(diet.get('foods_to_eat', []))} foods to eat, {len(diet.get('foods_to_avoid', []))} to avoid")
            
            # Success criteria: Should detect the disease
            expected_keywords = {
                'diabetes': ['Diabetes', 'glucose'],
                'hypertension': ['Hypertension', 'Blood Pressure'],
                'thyroid': ['Thyroid', 'TSH'],
                'kidney': ['Kidney', 'Creatinine']
            }
            
            expected_kwords = expected_keywords.get(disease_type, [])
            if any(kw in disease_detected for kw in expected_kwords):
                print(f"\n✅ CORRECT: Detected {disease_detected}")
                return True
            else:
                print(f"\n⚠️ PARTIAL: Got '{disease_detected}' - AI vision may need improvement")
                return False
        else:
            print(f"❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False
    finally:
        # Cleanup
        for f in [img_filename, generic_filename]:
            try:
                os.remove(f)
            except:
                pass


def main():
    print("\n" + "="*60)
    print("🔬 ADVANCED OCR + PATTERN MATCHING TEST SUITE")
    print("Testing AI Vision Detection (without filename keywords)")
    print("="*60)
    
    # Wait for server
    print("\nWaiting for server...")
    for i in range(10):
        try:
            requests.get(f"{BASE_URL}/", timeout=2)
            print("✅ Server ready!\n")
            break
        except:
            if i < 9:
                time.sleep(1)
    
    # Run tests
    diseases = ['diabetes', 'hypertension', 'thyroid', 'kidney']
    results = []
    
    for disease in diseases:
        result = test_ai_vision_detection(disease)
        results.append((disease, result))
        time.sleep(2)
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"Passed: {passed}/{total}\n")
    for disease, result in results:
        status = "✅" if result else "⚠️"
        print(f"{status} {disease.capitalize()}")
    
    if passed >= 2:
        print("\n✅ Good! AI vision is detecting diseases from medical report text.")
    else:
        print("\n⚠️ AI vision needs improvement. Consider using Vision API for better accuracy.")


if __name__ == '__main__':
    main()
