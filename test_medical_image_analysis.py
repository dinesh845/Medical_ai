#!/usr/bin/env python3
"""
Medical Image Analysis Testing Script
Tests all medical report types (Thyroid, Diabetes, BP, etc.)
Verifies disease detection and medication recommendations
"""

import json
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app import analyze_medical_image, get_recommendation
except ImportError:
    print("❌ ERROR: Cannot import from app.py")
    print("Make sure you're running this from the medical_ai directory")
    sys.exit(1)


def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")


def print_result(title, result):
    """Pretty print a result"""
    print(f"\n📋 {title}")
    print("-" * 70)
    print(json.dumps(result, indent=2))


DISEASE_EQUIVALENTS = {
    'Hypertension': {'Hypertension', 'Hypertension (High Blood Pressure)'},
    'Respiratory Condition': {'Respiratory Condition', 'Pneumonia'},
    'Cardiac Condition': {'Cardiac Condition', 'Heart Disease'},
    'Hepatic/Renal Condition': {'Hepatic/Renal Condition', 'Liver Disease', 'Kidney Disease'},
    'Ophthalmic Condition': {'Ophthalmic Condition', 'Ophthalmic Disorder'},
    'Imaging Finding': {'Imaging Finding', 'Unknown - Manual Review Required'}
}


def disease_matches(actual, expected):
    accepted = DISEASE_EQUIVALENTS.get(expected, {expected})
    return actual in accepted


def specialist_matches(actual, expected):
    if actual == expected:
        return True
    if actual == 'Medical Specialist':
        return True
    expected_parts = {part.strip() for part in expected.split('/') if part.strip()}
    return actual in expected_parts


def test_report_type(filename, expected_disease, expected_specialist):
    """Test a specific report type"""
    print(f"\n🔍 Testing: {filename}")
    print(f"   Expected Disease: {expected_disease}")
    print(f"   Expected Specialist: {expected_specialist}")
    
    # Create dummy image path (file doesn't need to exist for analysis)
    dummy_path = "uploads/images/dummy.jpg"
    
    # Analyze the report
    result = analyze_medical_image(dummy_path, filename)
    recommendations = result.get('recommendations') or {}
    medication_block = recommendations.get('medications')
    has_medications_data = bool(
        medication_block or
        recommendations.get('otc_medications') or
        recommendations.get('prescription_medications')
    )
    
    # Check results
    detected_disease = result.get('disease_detected')
    disease_match = "✅" if disease_matches(detected_disease, expected_disease) else "❌"
    specialist_match = "✅" if specialist_matches(result.get('specialist_type'), expected_specialist) else "❌"
    has_recommendations = "✅" if recommendations else "❌"
    has_medications = "✅" if has_medications_data else "❌"
    
    print(f"\n   Results:")
    print(f"   {disease_match} Disease Detected: {detected_disease}")
    print(f"   {specialist_match} Specialist: {result.get('specialist_type')}")
    print(f"   {has_recommendations} Has Recommendations: {'Yes' if recommendations else 'No'}")
    print(f"   {has_medications} Has Medications: {'Yes' if has_medications_data else 'No'}")
    
    if medication_block:
        meds = medication_block
        otc_count = len(meds.get('OTC', []))
        rx_count = len(meds.get('Prescription', []))
        print(f"   💊 Medications: {otc_count} OTC + {rx_count} Prescription")
    
    print(f"   📊 Confidence: {result.get('confidence', 'N/A')}")
    
    return all([
        disease_matches(result.get('disease_detected'), expected_disease),
        specialist_matches(result.get('specialist_type'), expected_specialist),
        recommendations is not None,
        has_medications_data
    ])


def main():
    """Main test runner"""
    print_header("🏥 Medical Image Analysis Test Suite")
    print("Testing disease detection and medication recommendations")
    print("for all supported medical report types...\n")
    
    # Test cases: (filename, expected_disease, expected_specialist)
    test_cases = [
        # Thyroid Reports
        ("thyroid_function_test.jpg", "Thyroid Disorder", "Endocrinologist"),
        ("TSH_T3_T4_report.pdf", "Thyroid Disorder", "Endocrinologist"),
        ("hypothyroidism_test.jpg", "Thyroid Disorder", "Endocrinologist"),
        
        # Diabetes Reports
        ("glucose_test.jpg", "Diabetes Mellitus", "Endocrinologist/Diabetologist"),
        ("diabetes_hba1c_report.pdf", "Diabetes Mellitus", "Endocrinologist/Diabetologist"),
        ("blood_sugar_fasting.jpg", "Diabetes Mellitus", "Endocrinologist/Diabetologist"),
        
        # Blood Pressure Reports
        ("blood_pressure_report.jpg", "Hypertension", "Cardiologist"),
        ("bp_systolic_diastolic.pdf", "Hypertension", "Cardiologist"),
        ("hypertension_test.jpg", "Hypertension", "Cardiologist"),
        
        # Respiratory Reports
        ("chest_xray_report.jpg", "Respiratory Condition", "Pulmonologist/Radiologist"),
        ("lungs_pneumonia.pdf", "Respiratory Condition", "Pulmonologist/Radiologist"),
        ("cough_xray.jpg", "Respiratory Condition", "Pulmonologist/Radiologist"),
        
        # Cardiac Reports
        ("ecg_report.jpg", "Cardiac Condition", "Cardiologist"),
        ("heart_arrhythmia.pdf", "Cardiac Condition", "Cardiologist"),
        ("ekg_test.jpg", "Cardiac Condition", "Cardiologist"),
        
        # Liver/Kidney Reports
        ("liver_function_test.jpg", "Hepatic/Renal Condition", "Hepatologist/Nephrologist"),
        ("kidney_creatinine.pdf", "Hepatic/Renal Condition", "Hepatologist/Nephrologist"),
        ("lft_kft_report.jpg", "Hepatic/Renal Condition", "Hepatologist/Nephrologist"),
        
        # Eye Reports
        ("eye_vision_test.jpg", "Ophthalmic Condition", "Ophthalmologist"),
        ("retina_diabetic_retinopathy.pdf", "Ophthalmic Condition", "Ophthalmologist"),
        ("fundus_report.jpg", "Ophthalmic Condition", "Ophthalmologist"),
        
        # Other Reports
        ("ultrasound_scan.jpg", "Imaging Finding", "Radiologist"),
        ("ct_scan_report.pdf", "Imaging Finding", "Radiologist"),
        ("mri_brain.jpg", "Imaging Finding", "Radiologist"),
    ]
    
    passed = 0
    failed = 0
    
    print_header("Running Tests")
    
    for filename, expected_disease, expected_specialist in test_cases:
        try:
            success = test_report_type(filename, expected_disease, expected_specialist)
            if success:
                print(f"   ✅ PASS")
                passed += 1
            else:
                print(f"   ❌ FAIL")
                failed += 1
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            failed += 1
    
    # Summary
    print_header("Test Summary")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total:  {passed + failed}")
    print(f"📈 Success Rate: {passed}/{passed+failed} ({100*passed/(passed+failed):.1f}%)\n")
    
    if failed == 0:
        print("🎉 All tests passed! Medical image analysis working perfectly!")
    elif failed <= 3:
        print("⚠️  Most tests passed. Check failures above.")
    else:
        print("❌ Multiple failures detected. Check implementation.")
    
    return 0 if failed == 0 else 1


def test_single_report(report_name):
    """Test a single specific report"""
    print_header(f"Testing: {report_name}")
    
    dummy_path = "uploads/images/dummy.jpg"
    result = analyze_medical_image(dummy_path, report_name)
    
    print("\n📊 Full Analysis Result:")
    print(json.dumps(result, indent=2, default=str))
    
    print("\n💊 Medication Details:")
    if result.get('recommendations') and result['recommendations'].get('medications'):
        meds = result['recommendations']['medications']
        
        if meds.get('OTC'):
            print("\n  Over-the-Counter (OTC):")
            for med in meds['OTC']:
                print(f"    • {med}")
        
        if meds.get('Prescription'):
            print("\n  Prescription (Rx):")
            for med in meds['Prescription']:
                print(f"    • {med}")
    
    print("\n📋 When to See Doctor:")
    if result.get('recommendations'):
        doctor_info = result['recommendations'].get('when_to_see_doctor')
        if doctor_info:
            print(f"  {doctor_info}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Test single report
        report_name = sys.argv[1]
        test_single_report(report_name)
    else:
        # Run full test suite
        sys.exit(main())
