#!/usr/bin/env python3
"""
Medical Image Analysis Testing Script (Simple - No Unicode)
Tests all medical report types
"""

import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app import analyze_medical_image, get_recommendation
except ImportError:
    print("ERROR: Cannot import from app.py")
    sys.exit(1)


def test_report(filename, expected_disease):
    """Test a specific report type"""
    dummy_path = "uploads/images/dummy.jpg"
    result = analyze_medical_image(dummy_path, filename)
    
    disease_aliases = {
        'Hypertension': {'Hypertension', 'Hypertension (High Blood Pressure)'},
        'Respiratory Condition': {'Respiratory Condition', 'Pneumonia'},
        'Cardiac Condition': {'Cardiac Condition', 'Heart Disease'},
        'Liver/Kidney Condition': {'Liver/Kidney Condition', 'Liver Disease', 'Kidney Disease'},
        'Ophthalmic Condition': {'Ophthalmic Condition', 'Ophthalmic Disorder'},
        'Imaging Finding': {'Imaging Finding', 'Unknown - Manual Review Required'}
    }
    accepted = disease_aliases.get(expected_disease, {expected_disease})
    disease_match = result.get('disease_detected') in accepted
    recommendations = result.get('recommendations') or {}
    has_meds = bool(
        recommendations.get('medications') or
        recommendations.get('otc_medications') or
        recommendations.get('prescription_medications')
    )
    has_specialist = result.get('specialist_type') is not None
    
    return disease_match and has_meds and has_specialist


def main():
    """Run all tests"""
    print("\nMEDICAL IMAGE ANALYSIS TEST SUITE")
    print("="*70)
    
    # Test cases
    tests = [
        ("thyroid_function_test.jpg", "Thyroid Disorder"),
        ("TSH_T3_T4_report.pdf", "Thyroid Disorder"),
        ("glucose_test.jpg", "Diabetes Mellitus"),
        ("diabetes_hba1c_report.pdf", "Diabetes Mellitus"),
        ("blood_pressure_report.jpg", "Hypertension"),
        ("bp_systolic_diastolic.pdf", "Hypertension"),
        ("chest_xray_report.jpg", "Respiratory Condition"),
        ("lungs_pneumonia.pdf", "Respiratory Condition"),
        ("ecg_report.jpg", "Cardiac Condition"),
        ("heart_arrhythmia.pdf", "Cardiac Condition"),
        ("liver_function_test.jpg", "Liver/Kidney Condition"),
        ("kidney_creatinine.pdf", "Liver/Kidney Condition"),
        ("eye_vision_test.jpg", "Ophthalmic Condition"),
        ("retina_diabetic_retinopathy.pdf", "Ophthalmic Condition"),
        ("ultrasound_scan.jpg", "Imaging Finding"),
        ("ct_scan_report.pdf", "Imaging Finding"),
    ]
    
    passed = 0
    failed = 0
    
    for filename, expected_disease in tests:
        success = test_report(filename, expected_disease)
        status = "[PASS]" if success else "[FAIL]"
        passed += success
        failed += (1 - success)
        print(f"{status} {filename:35} -> {expected_disease}")
    
    # Summary
    print("="*70)
    print(f"Results: {passed} PASSED, {failed} FAILED, {passed+failed} TOTAL")
    print(f"Success Rate: {100*passed/(passed+failed):.1f}%")
    print("="*70)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
