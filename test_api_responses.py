#!/usr/bin/env python3
"""
Test API Response for Medical Report Upload
Shows exactly what the system returns when uploading a thyroid report
"""

import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import analyze_medical_image, analyze_symptoms, get_recommendation

def test_thyroid_upload():
    """Simulate uploading a thyroid report"""
    print("\n" + "="*70)
    print("SIMULATING THYROID REPORT UPLOAD")
    print("="*70)
    
    # Image analysis (as if user uploaded thyroid_report.jpg)
    image_result = analyze_medical_image("uploads/images/dummy.jpg", "brother_thyroid_report.jpg")
    
    print("\nAPI RESPONSE for Thyroid Report Upload:")
    print("-"*70)
    print(json.dumps(image_result, indent=2, default=str))
    
    print("\n\n" + "="*70)
    print("EXTRACTED MEDICATIONS")
    print("="*70)
    
    if image_result.get('recommendations'):
        meds = image_result['recommendations'].get('medications', {})
        
        print("\nOTC (Over-the-Counter) Medications:")
        if isinstance(meds.get('OTC'), list):
            for med in meds['OTC']:
                print(f"  - {med}")
        else:
            print(f"  {meds.get('OTC')}")
        
        print("\nPrescription (Rx) Medications:")
        if isinstance(meds.get('Prescription'), list):
            for med in meds['Prescription']:
                print(f"  - {med}")
        else:
            print(f"  {meds.get('Prescription')}")
    
    print("\n\n" + "="*70)
    print("DETAILED RECOMMENDATIONS")
    print("="*70)
    
    if image_result.get('recommendations'):
        rec = image_result['recommendations']
        print(f"\nDisease: {image_result.get('disease_detected')}")
        print(f"Specialist: {image_result.get('specialist_type')}")
        print(f"Description: {rec.get('description')}")
        print(f"Duration: {rec.get('duration')}")
        print(f"Severity: {rec.get('severity_level')}")
        print(f"\nWhen to see doctor: {rec.get('when_to_see_doctor')}")
        
        print("\nRecommendations:")
        for i, r in enumerate(rec.get('recommendations', []), 1):
            print(f"  {i}. {r}")


def test_diabetes_upload():
    """Simulate uploading a diabetes report"""
    print("\n\n" + "="*70)
    print("SIMULATING DIABETES REPORT UPLOAD")
    print("="*70)
    
    # Image analysis
    image_result = analyze_medical_image("uploads/images/dummy.jpg", "sister_diabetes_glucose_test.jpg")
    
    print("\nAPI RESPONSE for Diabetes Report Upload:")
    print("-"*70)
    print(json.dumps(image_result, indent=2, default=str))
    
    print("\n\nExtracted Medications:")
    if image_result.get('recommendations'):
        meds = image_result['recommendations'].get('medications', {})
        print("OTC:", meds.get('OTC', [])[:2])  # First 2
        print("Rx:", meds.get('Prescription', [])[:3])  # First 3


def test_bp_upload():
    """Simulate uploading a blood pressure report"""
    print("\n\n" + "="*70)
    print("SIMULATING BLOOD PRESSURE REPORT UPLOAD")
    print("="*70)
    
    # Image analysis
    image_result = analyze_medical_image("uploads/images/dummy.jpg", "dad_blood_pressure_hypertension.jpg")
    
    print("\nAPI RESPONSE for Blood Pressure Report Upload:")
    print("-"*70)
    print(json.dumps(image_result, indent=2, default=str))


def test_combined_analysis():
    """Simulate combined text + image analysis"""
    print("\n\n" + "="*70)
    print("COMBINED ANALYSIS: Symptoms + Thyroid Report")
    print("="*70)
    
    # Symptom analysis
    symptoms_data = {
        'symptoms': 'fatigue, weight gain, feeling cold, dry skin, hair loss',
        'severity': 'moderate',
        'duration': '2 months'
    }
    
    symptoms_result = analyze_symptoms(symptoms_data)
    
    # Image analysis
    image_result = analyze_medical_image("uploads/images/dummy.jpg", "thyroid_TSH_report.jpg")
    
    print("\nSymptom Analysis Result:")
    print(json.dumps(symptoms_result, indent=2, default=str)[:400] + "...")
    
    print("\n\nImage Analysis Result:")
    print(json.dumps(image_result, indent=2, default=str)[:400] + "...")
    
    print("\n\nCombined Findings:")
    symptom_conditions = symptoms_result.get('possible_conditions') or symptoms_result.get('conditions', [])
    print(f"  From Symptoms: {symptom_conditions[0:2]} ")
    print(f"  From Report: {image_result['disease_detected']}")
    print(f"  Confidence: {image_result['confidence']}")
    print(f"  Specialist: {image_result['specialist_type']}")


if __name__ == "__main__":
    test_thyroid_upload()
    test_diabetes_upload()
    test_bp_upload()
    test_combined_analysis()
    
    print("\n\n" + "="*70)
    print("ALL SIMULATIONS COMPLETE")
    print("="*70)
    print("\nYour Medical AI System is ready to:")
    print("  1. Detect medical reports by filename")
    print("  2. Identify disease type")
    print("  3. Return medication recommendations")
    print("  4. Provide specialist referrals")
    print("  5. Give 'when to see doctor' guidance")
    print("\nStart the Flask server and upload your brother's thyroid report now!")
    print("="*70)
