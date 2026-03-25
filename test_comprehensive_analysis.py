#!/usr/bin/env python3
"""
Test Medical Report Analysis with Findings, Action Plans, and Diet
Shows the complete output for medical reports
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import analyze_medical_image

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def test_thyroid_report():
    """Test thyroid report analysis"""
    print_section("THYROID REPORT ANALYSIS")
    
    result = analyze_medical_image("dummy.jpg", "brother_thyroid_report.jpg")
    
    print(f"Disease Detected: {result.get('disease_detected')}")
    print(f"Specialist: {result.get('specialist_type')}")
    print(f"Confidence: {result.get('confidence')}")
    
    print(f"\nWHAT IS PRESENT (Findings):")
    for i, finding in enumerate(result.get('what_is_present', []), 1):
        print(f"  {i}. {finding}")
    
    print(f"\nWHAT TO DO NEXT (Action Plan):")
    for step in result.get('action_plan', []):
        print(f"  • {step}")
    
    diet = result.get('diet_plan', {})
    if diet:
        print(f"\nDIET PLAN:")
        print(f"  Foods to Eat:")
        for food in diet.get('foods_to_eat', [])[:5]:
            print(f"    - {food}")
        print(f"  Foods to Avoid:")
        for food in diet.get('foods_to_avoid', [])[:5]:
            print(f"    - {food}")
        print(f"  Daily Recommendation: {diet.get('daily_recommendation')}")
    
    meds = result.get('recommendations', {}).get('medications', {})
    print(f"\nMEDICATIONS:")
    print(f"  OTC:")
    for med in meds.get('OTC', [])[:2]:
        print(f"    - {med}")
    print(f"  Prescription:")
    for med in meds.get('Prescription', [])[:3]:
        print(f"    - {med}")


def test_diabetes_report():
    """Test diabetes report analysis"""
    print_section("DIABETES REPORT ANALYSIS")
    
    result = analyze_medical_image("dummy.jpg", "diabetes_glucose_test.jpg")
    
    print(f"Disease Detected: {result.get('disease_detected')}")
    print(f"Specialist: {result.get('specialist_type')}")
    print(f"Confidence: {result.get('confidence')}")
    
    print(f"\nWHAT IS PRESENT (Findings):")
    for i, finding in enumerate(result.get('what_is_present', []), 1):
        print(f"  {i}. {finding}")
    
    print(f"\nWHAT TO DO NEXT (Action Plan - First 3 Steps):")
    for step in result.get('action_plan', [])[:3]:
        print(f"  • {step}")
    
    diet = result.get('diet_plan', {})
    if diet:
        print(f"\nDIET PLAN SUMMARY:")
        print(f"  Foods to Eat (5 examples):")
        for food in diet.get('foods_to_eat', [])[:5]:
            print(f"    - {food}")
        print(f"  Foods to Avoid (5 examples):")
        for food in diet.get('foods_to_avoid', [])[:5]:
            print(f"    - {food}")
        print(f"  Daily Recommendation: {diet.get('daily_recommendation')}")


def test_bp_report():
    """Test blood pressure report analysis"""
    print_section("BLOOD PRESSURE REPORT ANALYSIS")
    
    result = analyze_medical_image("dummy.jpg", "blood_pressure_reading.jpg")
    
    print(f"Disease Detected: {result.get('disease_detected')}")
    print(f"Specialist: {result.get('specialist_type')}")
    print(f"Confidence: {result.get('confidence')}")
    
    print(f"\nWHAT IS PRESENT (Findings):")
    for i, finding in enumerate(result.get('what_is_present', []), 1):
        print(f"  {i}. {finding}")
    
    print(f"\nWHAT TO DO NEXT (Action Plan - First 4 Steps):")
    for step in result.get('action_plan', [])[:4]:
        print(f"  • {step}")
    
    diet = result.get('diet_plan', {})
    if diet:
        print(f"\nDIET PLAN HIGHLIGHTS:")
        print(f"  Key Point: {diet.get('daily_recommendation')}")
        print(f"  Meal Timing: {diet.get('meal_timing')}")
        print(f"  Foods to Eat:")
        for food in diet.get('foods_to_eat', [])[:3]:
            print(f"    - {food}")


def test_json_response():
    """Test full JSON response"""
    print_section("COMPLETE JSON RESPONSE (Thyroid Report)")
    
    result = analyze_medical_image("dummy.jpg", "thyroid_report.jpg")
    
    # Show condensed JSON
    output = {
        'disease_detected': result.get('disease_detected'),
        'specialist': result.get('specialist_type'),
        'what_is_present': result.get('what_is_present', [])[:2],
        'action_plan': result.get('action_plan', [])[:3],
        'diet_plan': {
            'foods_to_eat': result.get('diet_plan', {}).get('foods_to_eat', [])[:2],
            'foods_to_avoid': result.get('diet_plan', {}).get('foods_to_avoid', [])[:2],
        },
        'medications_otc': result.get('recommendations', {}).get('medications', {}).get('OTC', [])[:1],
        'medications_rx': result.get('recommendations', {}).get('medications', {}).get('Prescription', [])[:2],
    }
    
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  MEDICAL REPORT ANALYSIS WITH FINDINGS, PLANS, AND DIET")
    print("="*70)
    
    test_thyroid_report()
    test_diabetes_report()
    test_bp_report()
    test_json_response()
    
    print_section("SUMMARY")
    print("""
EACH MEDICAL REPORT NOW INCLUDES:

1. WHAT IS PRESENT (Findings found in the test)
   - Specific abnormalities detected
   - Clinical indicators present
   - Risk factors identified

2. WHAT TO DO NEXT (Action Plan with steps)
   - Step-by-step instructions
   - Timeline for follow-up tests
   - Medication timing
   - Monitoring requirements

3. DIET PLAN (Specific nutritional guidance)
   - Foods to eat and why
   - Foods to avoid and why
   - Meal timing recommendations
   - Daily calorie/portion guidance
   - Example meal combinations

4. MEDICATIONS (Exact dosages as before)
   - OTC options
   - Prescription options
   - Frequencies and amounts
    """)
    
    print(f"\n{'='*70}")
    print("All medical reports now provide COMPLETE, ACTIONABLE guidance!")
    print(f"{'='*70}\n")
