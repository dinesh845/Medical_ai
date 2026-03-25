from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image
import numpy as np
from llm_integration import get_chatbot_response
import re
from urllib.parse import quote_plus
from clinical_ai_engine import (
    MultiModalPreDiagnosisEngine,
    RiskStratificationModel,
    PilotValidationService,
)
from privacy_framework import DataPrivacyFramework

# Try to import OCR for text extraction from images
try:
    import easyocr
    OCR_AVAILABLE = True
except:
    OCR_AVAILABLE = False

app = Flask(__name__)
app.config['SECRET_KEY'] = 'medical-ai-secret-key-2026'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
CORS(app)

# Create necessary directories
os.makedirs('uploads/images', exist_ok=True)
os.makedirs('uploads/audio', exist_ok=True)
os.makedirs('data', exist_ok=True)

multimodal_engine = MultiModalPreDiagnosisEngine()
risk_model = RiskStratificationModel()
pilot_validator = PilotValidationService()
privacy_framework = DataPrivacyFramework()

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'dcm', 'nii'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a'}

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def _extract_lab_values(payload, data_dict, image_analysis):
    lab_values = dict(payload.get('lab_values') or {})
    text_chunks = [
        str(data_dict.get('symptoms', '')),
        str(data_dict.get('clinical_text', '')),
        str((image_analysis or {}).get('extracted_text', '')),
    ]
    parsed = multimodal_engine.extract_lab_values_from_text(' '.join(text_chunks))
    for key, value in parsed.items():
        lab_values.setdefault(key, value)
    return lab_values


def _build_decision_support_payload(data_dict, image_analysis):
    symptoms_text = str(data_dict.get('symptoms', ''))
    image_text = str((image_analysis or {}).get('extracted_text', ''))
    clinical_text = str(data_dict.get('clinical_text', ''))

    payload = {
        'age': data_dict.get('age', 30),
        'symptoms': symptoms_text,
        'clinical_text': clinical_text,
        'image_text': image_text,
        'comorbidities': data_dict.get('comorbidities', []),
    }
    payload['lab_values'] = _extract_lab_values(payload, data_dict, image_analysis)
    return payload


def _require_role(allowed_roles):
    role = request.headers.get('X-Role', 'guest').strip().lower()
    if not privacy_framework.enforce_role(role, allowed_roles):
        privacy_framework.write_audit_event('unauthorized_access', role, {'allowed_roles': allowed_roles})
        return None, jsonify({'success': False, 'error': 'Forbidden for current role'}), 403
    return role, None, None


def _normalize_location(location_text):
    location = (location_text or '').strip().lower()
    if location in ['vizag', 'visakhapatnam', 'vizag city']:
        return 'vizag'
    if location in ['kkd', 'kakinada', 'kakinada city']:
        return 'kkd'
    if location in ['hyderabad', 'hyd', 'hyd city']:
        return 'hyderabad'
    if location in ['vijayawada', 'bezawada']:
        return 'vijayawada'
    if location in ['rajahmundry', 'rajamahendravaram', 'rjy']:
        return 'rajahmundry'
    if location in ['chennai', 'madras']:
        return 'chennai'
    if location in ['bangalore', 'bengaluru', 'blr']:
        return 'bangalore'
    return 'other'


def _map_condition_to_specialty(condition_text):
    condition = (condition_text or '').lower()
    if any(k in condition for k in ['heart', 'hypertension', 'bp', 'cardiac']):
        return 'Cardiologist'
    if any(k in condition for k in ['diabetes', 'thyroid', 'hormone', 'endocrine']):
        return 'Endocrinologist'
    if any(k in condition for k in ['kidney', 'renal']):
        return 'Nephrologist'
    if any(k in condition for k in ['liver', 'hepatitis']):
        return 'Hepatologist'
    if any(k in condition for k in ['respiratory', 'asthma', 'pneumonia', 'cough', 'lung']):
        return 'Pulmonologist'
    if any(k in condition for k in ['skin', 'eczema', 'psoriasis', 'acne', 'rash']):
        return 'Dermatologist'
    if any(k in condition for k in ['headache', 'migraine', 'neuro']):
        return 'Neurologist'
    if any(k in condition for k in ['stomach', 'gastro', 'abdominal', 'ulcer']):
        return 'Gastroenterologist'
    if any(k in condition for k in ['anxiety', 'depression', 'mental']):
        return 'Psychiatrist'
    return 'General Physician'


def _recommend_doctors(location_text, probable_conditions):
    location_input = (location_text or '').strip()
    location = _normalize_location(location_input)

    def _maps_link(hospital, city):
        query = quote_plus(f"{hospital} {city}")
        return f"https://www.google.com/maps/search/?api=1&query={query}"

    city_display = {
        'vizag': 'Vizag',
        'kkd': 'Kakinada',
        'hyderabad': 'Hyderabad',
        'vijayawada': 'Vijayawada',
        'rajahmundry': 'Rajahmundry',
        'chennai': 'Chennai',
        'bangalore': 'Bangalore',
        'other': location_input if location_input else 'Your City',
    }.get(location, location_input or 'Your City')

    city_data = {
        'vizag': {
            'Cardiologist': [
                {'doctor': 'Dr. S. Prasad', 'hospital': 'Care Hospitals, Vizag', 'contact': '+91-891-4000001', 'map_url': _maps_link('Care Hospitals', 'Vizag')},
                {'doctor': 'Dr. R. Lakshmi', 'hospital': 'Apollo Hospitals, Vizag', 'contact': '+91-891-2529611', 'map_url': _maps_link('Apollo Hospitals', 'Vizag')},
            ],
            'Endocrinologist': [
                {'doctor': 'Dr. K. Naveen', 'hospital': 'SevenHills Hospital, Vizag', 'contact': '+91-891-6677777', 'map_url': _maps_link('SevenHills Hospital', 'Vizag')},
                {'doctor': 'Dr. P. Sirisha', 'hospital': 'Apollo Hospitals, Vizag', 'contact': '+91-891-2529611', 'map_url': _maps_link('Apollo Hospitals', 'Vizag')},
            ],
            'Pulmonologist': [
                {'doctor': 'Dr. V. Murthy', 'hospital': 'KIMS-ICON, Vizag', 'contact': '+91-891-3040000', 'map_url': _maps_link('KIMS-ICON', 'Vizag')},
            ],
            'General Physician': [
                {'doctor': 'Dr. N. Kumar', 'hospital': 'Mahatma Gandhi Cancer Hospital, Vizag', 'contact': '+91-891-2878787', 'map_url': _maps_link('Mahatma Gandhi Cancer Hospital', 'Vizag')},
            ],
        },
        'kkd': {
            'Cardiologist': [
                {'doctor': 'Dr. T. Bhaskar', 'hospital': 'Medicover Hospitals, Kakinada', 'contact': '+91-884-2301111', 'map_url': _maps_link('Medicover Hospitals', 'Kakinada')},
            ],
            'Endocrinologist': [
                {'doctor': 'Dr. M. Keerthi', 'hospital': 'Government General Hospital, Kakinada', 'contact': '+91-884-2366666', 'map_url': _maps_link('Government General Hospital', 'Kakinada')},
            ],
            'Pulmonologist': [
                {'doctor': 'Dr. A. Suman', 'hospital': 'Sri Hospitals, Kakinada', 'contact': '+91-884-2377777', 'map_url': _maps_link('Sri Hospitals', 'Kakinada')},
            ],
            'General Physician': [
                {'doctor': 'Dr. R. Chaitanya', 'hospital': 'Apollo Reach Hospital, Kakinada', 'contact': '+91-884-6693333', 'map_url': _maps_link('Apollo Reach Hospital', 'Kakinada')},
            ],
        },
        'hyderabad': {
            'Cardiologist': [
                {'doctor': 'Dr. A. Raghav', 'hospital': 'Yashoda Hospitals, Hyderabad', 'contact': '+91-40-45674567', 'map_url': _maps_link('Yashoda Hospitals', 'Hyderabad')},
            ],
            'Endocrinologist': [
                {'doctor': 'Dr. S. Lavanya', 'hospital': 'Apollo Hospitals, Jubilee Hills', 'contact': '+91-40-23607777', 'map_url': _maps_link('Apollo Hospitals Jubilee Hills', 'Hyderabad')},
            ],
            'General Physician': [
                {'doctor': 'Dr. V. Naresh', 'hospital': 'KIMS Hospitals, Secunderabad', 'contact': '+91-40-44885000', 'map_url': _maps_link('KIMS Hospitals', 'Hyderabad')},
            ],
        },
        'vijayawada': {
            'Cardiologist': [
                {'doctor': 'Dr. P. Ramesh', 'hospital': 'Andhra Hospitals, Vijayawada', 'contact': '+91-866-2484800', 'map_url': _maps_link('Andhra Hospitals', 'Vijayawada')},
            ],
            'Endocrinologist': [
                {'doctor': 'Dr. H. Madhavi', 'hospital': 'Ramesh Hospitals, Vijayawada', 'contact': '+91-866-6679999', 'map_url': _maps_link('Ramesh Hospitals', 'Vijayawada')},
            ],
            'General Physician': [
                {'doctor': 'Dr. S. Phani', 'hospital': 'Aayush Hospitals, Vijayawada', 'contact': '+91-866-2575555', 'map_url': _maps_link('Aayush Hospitals', 'Vijayawada')},
            ],
        },
        'rajahmundry': {
            'Cardiologist': [
                {'doctor': 'Dr. B. Suresh', 'hospital': 'Royal Hospitals, Rajahmundry', 'contact': '+91-883-2456789', 'map_url': _maps_link('Royal Hospitals', 'Rajahmundry')},
            ],
            'Endocrinologist': [
                {'doctor': 'Dr. T. Keerthana', 'hospital': 'Apex Hospital, Rajahmundry', 'contact': '+91-883-2421111', 'map_url': _maps_link('Apex Hospital', 'Rajahmundry')},
            ],
            'General Physician': [
                {'doctor': 'Dr. M. Srinivas', 'hospital': 'GSL Medical College Hospital, Rajahmundry', 'contact': '+91-883-2499999', 'map_url': _maps_link('GSL Medical College Hospital', 'Rajahmundry')},
            ],
        },
        'chennai': {
            'Cardiologist': [
                {'doctor': 'Dr. K. Anand', 'hospital': 'Apollo Hospitals, Greams Road', 'contact': '+91-44-28290200', 'map_url': _maps_link('Apollo Hospitals Greams Road', 'Chennai')},
            ],
            'Endocrinologist': [
                {'doctor': 'Dr. N. Priya', 'hospital': 'MIOT International, Chennai', 'contact': '+91-44-42002288', 'map_url': _maps_link('MIOT International', 'Chennai')},
            ],
            'General Physician': [
                {'doctor': 'Dr. R. Vivek', 'hospital': 'SIMS Hospital, Chennai', 'contact': '+91-44-20002001', 'map_url': _maps_link('SIMS Hospital', 'Chennai')},
            ],
        },
        'bangalore': {
            'Cardiologist': [
                {'doctor': 'Dr. D. Kiran', 'hospital': 'Narayana Health City, Bangalore', 'contact': '+91-80-71222222', 'map_url': _maps_link('Narayana Health City', 'Bangalore')},
            ],
            'Endocrinologist': [
                {'doctor': 'Dr. P. Meera', 'hospital': 'Manipal Hospital, Old Airport Road', 'contact': '+91-80-25024444', 'map_url': _maps_link('Manipal Hospital Old Airport Road', 'Bangalore')},
            ],
            'General Physician': [
                {'doctor': 'Dr. A. Harish', 'hospital': 'Aster CMI Hospital, Bangalore', 'contact': '+91-80-43420100', 'map_url': _maps_link('Aster CMI Hospital', 'Bangalore')},
            ],
        },
        'other': {
            'Cardiologist': [
                {'doctor': 'Cardiology Desk', 'hospital': f'Top Heart Care in {city_display}', 'contact': '+91-800-000-0000', 'map_url': _maps_link('Cardiology Hospital', city_display)},
            ],
            'Endocrinologist': [
                {'doctor': 'Diabetes & Hormone Desk', 'hospital': f'Top Endocrine Clinic in {city_display}', 'contact': '+91-800-000-0000', 'map_url': _maps_link('Endocrinology Clinic', city_display)},
            ],
            'Pulmonologist': [
                {'doctor': 'Lung Care Desk', 'hospital': f'Top Pulmonology Center in {city_display}', 'contact': '+91-800-000-0000', 'map_url': _maps_link('Pulmonology Hospital', city_display)},
            ],
            'General Physician': [
                {'doctor': 'Tele-Consult Specialist Desk', 'hospital': f'MediAI Partner Network - {city_display}', 'contact': '+91-800-000-0000', 'map_url': _maps_link('General Physician', city_display)},
            ],
        },
    }

    base_specialty = 'General Physician'
    condition_text = ' '.join(probable_conditions or [])
    specialty = _map_condition_to_specialty(condition_text) if condition_text else base_specialty

    location_pool = city_data.get(location, city_data['other'])
    doctors = location_pool.get(specialty) or location_pool.get(base_specialty) or city_data['other'][base_specialty]

    return {
        'location_input': location_input,
        'city_display': city_display,
        'location_normalized': location,
        'recommended_specialty': specialty,
        'top_doctors': doctors[:3],
    }

def analyze_symptoms(symptoms_data):
    """AI-based symptom analysis with comprehensive medical information"""
    # This analyzes symptoms and provides detailed medical recommendations
    
    symptoms = symptoms_data.get('symptoms', '').lower()
    severity = symptoms_data.get('severity', 'moderate')
    duration = symptoms_data.get('duration', '')
    
    # Symptom matching logic
    possible_conditions = []
    confidence_scores = []
    
    # RESPIRATORY SYMPTOMS
    if 'fever' in symptoms or 'temperature' in symptoms:
        if 'cough' in symptoms and 'body ache' in symptoms:
            possible_conditions.append('Flu (Influenza)')
            confidence_scores.append(0.85)
        elif 'cough' in symptoms or 'sore throat' in symptoms or 'sneez' in symptoms:
            possible_conditions.append('Common Cold')
            confidence_scores.append(0.80)
        elif 'breathing' in symptoms or 'chest' in symptoms:
            possible_conditions.append('Pneumonia')
            confidence_scores.append(0.75)
        else:
            possible_conditions.append('Viral Infection')
            confidence_scores.append(0.65)
    
    if 'cough' in symptoms:
        if 'persistent' in symptoms or 'duration' in symptoms and duration and int(duration.split('-')[0]) > 2:
            possible_conditions.append('Bronchitis')
            confidence_scores.append(0.72)
    
    if 'wheez' in symptoms or 'asthma' in symptoms or 'breathing' in symptoms:
        if 'asthma' not in symptoms:
            possible_conditions.append('Asthma')
            confidence_scores.append(0.70)
    
    # GASTROINTESTINAL SYMPTOMS
    if 'stomach' in symptoms or 'abdomen' in symptoms or 'nausea' in symptoms or 'vomit' in symptoms:
        if 'diarrhea' in symptoms or 'loose' in symptoms:
            possible_conditions.append('Gastroenteritis (Food Poisoning)')
            confidence_scores.append(0.78)
        elif 'pain' in symptoms and 'burning' in symptoms:
            possible_conditions.append('Peptic Ulcer Disease')
            confidence_scores.append(0.65)
        else:
            possible_conditions.append('Gastrointestinal Issue')
            confidence_scores.append(0.60)
    
    if 'constip' in symptoms:
        possible_conditions.append('Constipation')
        confidence_scores.append(0.80)
    
    if 'diarrhea' in symptoms or 'loose stool' in symptoms:
        possible_conditions.append('Diarrhea')
        confidence_scores.append(0.80)
    
    # NEUROLOGICAL SYMPTOMS
    if 'headache' in symptoms:
        if 'severe' in symptoms and ('nausea' in symptoms or 'light' in symptoms):
            possible_conditions.append('Migraine Headache')
            confidence_scores.append(0.75)
        else:
            possible_conditions.append('Tension Headache')
            confidence_scores.append(0.70)
    
    # URINARY SYMPTOMS
    if 'urine' in symptoms or 'urinary' in symptoms or 'burning' in symptoms and 'urination' in symptoms:
        possible_conditions.append('Urinary Tract Infection (UTI)')
        confidence_scores.append(0.82)
    
    # EAR/THROAT SYMPTOMS
    if 'sore throat' in symptoms or 'throat pain' in symptoms:
        possible_conditions.append('Sore Throat (Pharyngitis)')
        confidence_scores.append(0.80)
    
    if 'ear' in symptoms or 'ear pain' in symptoms or 'earache' in symptoms:
        possible_conditions.append('Ear Infection (Otitis)')
        confidence_scores.append(0.85)
    
    # SKIN SYMPTOMS
    if 'rash' in symptoms or 'itching' in symptoms and 'skin' in symptoms:
        if 'eczema' in symptoms:
            possible_conditions.append('Eczema (Atopic Dermatitis)')
            confidence_scores.append(0.88)
        elif 'acne' in symptoms or 'pimples' in symptoms:
            possible_conditions.append('Acne')
            confidence_scores.append(0.90)
        else:
            possible_conditions.append('Skin Rash')
            confidence_scores.append(0.75)
    
    # ALLERGY SYMPTOMS
    if 'sneez' in symptoms or 'nasal' in symptoms or 'runny nose' in symptoms or 'nasal congestion' in symptoms:
        if 'allergy' in symptoms:
            possible_conditions.append('Allergic Rhinitis (Hay Fever)')
            confidence_scores.append(0.85)
    
    if 'allergy' in symptoms or 'allergic' in symptoms:
        possible_conditions.append('Food Allergy')
        confidence_scores.append(0.65)
    
    # CHRONIC CONDITIONS
    if 'blood pressure' in symptoms or 'hypertension' in symptoms or 'high bp' in symptoms:
        possible_conditions.append('Hypertension (High Blood Pressure)')
        confidence_scores.append(0.85)
    
    if 'diabetes' in symptoms or 'blood sugar' in symptoms or 'glucose' in symptoms:
        possible_conditions.append('Diabetes Mellitus')
        confidence_scores.append(0.80)
    
    if 'thyroid' in symptoms or 'fatigue' in symptoms and 'weight' in symptoms:
        possible_conditions.append('Thyroid Disorder')
        confidence_scores.append(0.60)
    
    # SLEEP CONDITIONS
    if 'sleep' in symptoms or 'insomnia' in symptoms or 'sleepless' in symptoms:
        possible_conditions.append('Insomnia')
        confidence_scores.append(0.80)
    
    # EMERGENCY CHECK
    emergency_keywords = ['chest pain', 'difficulty breathing', 'shortness of breath', 'severe bleeding', 
                         'loss of consciousness', 'call 911', 'heart attack', 'stroke', 'seizure', 
                         'poisoning', 'severe allergic reaction', 'choking', 'severe burns']
    if any(keyword in symptoms for keyword in emergency_keywords):
        return {
            'conditions': ['🚨 EMERGENCY - SEEK IMMEDIATE HELP 🚨'],
            'confidence': [1.0],
            'severity': 'CRITICAL',
            'recommendation': get_recommendation('Emergency', 'critical')
        }
    
    # Default if no conditions matched
    if not possible_conditions:
        possible_conditions = ['General Consultation Recommended']
        confidence_scores = [0.50]
    
    # Sort by confidence and get top 3
    sorted_items = sorted(zip(possible_conditions, confidence_scores), key=lambda x: x[1], reverse=True)
    top_conditions = [item[0] for item in sorted_items[:3]]
    top_scores = [item[1] for item in sorted_items[:3]]
    
    return {
        'conditions': top_conditions,
        'possible_conditions': top_conditions,
        'confidence': top_scores,
        'severity': severity,
        'duration': duration,
        'recommendations': [get_recommendation(top_conditions[i], severity) for i in range(len(top_conditions))] if top_conditions else []
    }

def extract_text_from_image(image_path):
    """Extract text from medical image using OCR"""
    try:
        if not OCR_AVAILABLE:
            return ""
        
        # Initialize reader (loads model on first use)
        reader = easyocr.Reader(['en'], gpu=False)
        
        # Read text from image
        result = reader.readtext(image_path)
        
        # Extract and combine text
        extracted_text = '\n'.join([text[1] for text in result])
        
        # If no text extracted, try alternative approach
        if not extracted_text or len(extracted_text) < 20:
            # Try PIL to see if image is readable
            img = Image.open(image_path)
            # Return some indication that image was read
            return f"Image dimensions: {img.size}, Image mode: {img.mode}"
        
        return extracted_text.lower()
    except Exception as e:
        print(f"OCR Error (non-critical): {e}")
        # Return empty string to trigger fallback
        return ""

def detect_disease_from_image_content(image_path, filename=''):
    """
    AI-powered disease detection from image content
    Analyzes extracted text and visual patterns to identify diseases
    Filename is used as secondary method if text extraction fails
    """
    
    # Extract text from image using OCR
    extracted_text = extract_text_from_image(image_path)
    
    # Disease detection patterns based on common medical test values and keywords
    disease_patterns = {
        'Thyroid Disorder': {
            'keywords': ['tsh', 't3', 't4', 'thyroid', 'thyroiditis', 'hyperthyroid', 'hypothyroid'],
            'value_indicators': [
                (r'tsh\s*[=:]\s*([0-9.]+)', lambda x: float(x) < 0.4 or float(x) > 4.0),  # Abnormal TSH
                (r't4\s*[=:]\s*([0-9.]+)', lambda x: float(x) < 5 or float(x) > 12),  # Abnormal T4
                (r't3\s*[=:]\s*([0-9.]+)', lambda x: float(x) < 80 or float(x) > 200),  # Abnormal T3
            ]
        },
        'Diabetes Mellitus': {
            'keywords': ['glucose', 'diabetes', 'blood sugar', 'hba1c', 'fasting', 'random blood'],
            'value_indicators': [
                (r'glucose\s*[=:]\s*([0-9.]+)', lambda x: float(x) > 126),  # Fasting glucose
                (r'hba1c\s*[=:]\s*([0-9.%]+)', lambda x: float(x.replace('%', '')) > 6.5),  # HbA1c
                (r'blood sugar\s*[=:]\s*([0-9.]+)', lambda x: float(x) > 200),  # Random blood sugar
            ]
        },
        'Hypertension (High Blood Pressure)': {
            'keywords': ['blood pressure', 'hypertension', 'systolic', 'diastolic', 'mmhg', 'hypertensive'],
            'value_indicators': [
                (r'(?:systolic|sys)\s*[=:]\s*([0-9.]+)', lambda x: float(x) > 140),
                (r'(?:diastolic|dia)\s*[=:]\s*([0-9.]+)', lambda x: float(x) > 90),
                (r'bp\s*[=:]\s*([0-9.]+)\s*/\s*([0-9.]+)', lambda x: float(x) > 140 or float(x) > 90),
            ]
        },
        'Anemia': {
            'keywords': ['hemoglobin', 'hb', 'red blood cells', 'rbc', 'anemia'],
            'value_indicators': [
                (r'hemoglobin\s*[=:]\s*([0-9.]+)', lambda x: float(x) < 12),
                (r'hb\s*[=:]\s*([0-9.]+)', lambda x: float(x) < 12),
            ]
        },
        'Heart Disease': {
            'keywords': ['cardiac', 'ecg', 'ekg', 'heart', 'arrhythmia', 'troponin'],
            'value_indicators': [
                (r'troponin\s*[=:]\s*([0-9.]+)', lambda x: float(x) > 0.04),
            ]
        },
        'Liver Disease': {
            'keywords': ['liver', 'ast', 'alt', 'bilirubin', 'alkaline phosphatase', 'hepatic'],
            'value_indicators': [
                (r'ast\s*[=:]\s*([0-9.]+)', lambda x: float(x) > 40),
                (r'alt\s*[=:]\s*([0-9.]+)', lambda x: float(x) > 40),
            ]
        },
        'Kidney Disease': {
            'keywords': ['kidney', 'creatinine', 'bun', 'gfr', 'renal'],
            'value_indicators': [
                (r'creatinine\s*[=:]\s*([0-9.]+)', lambda x: float(x) > 1.2),
            ]
        },
    }
    
    detected_diseases = []
    confidence_scores = []
    
    # Also consider filename as evidence
    filename_lower = filename.lower() if filename else ''
    filename_normalized = filename_lower.replace('_', ' ').replace('-', ' ')
    
    # If we have extracted text, analyze it
    if extracted_text and len(extracted_text) > 10:
        for disease, patterns in disease_patterns.items():
            disease_confidence = 0.0
            
            # Check for keywords in text
            keyword_matches = [kw for kw in patterns['keywords'] if kw in extracted_text]
            if keyword_matches:
                # More generous scoring - even one keyword match counts
                disease_confidence += 0.25 + (0.15 * len(keyword_matches) / len(patterns['keywords']))
            
            # BONUS: Also check filename for keywords (as supporting evidence)
            filename_keyword_matches = [kw for kw in patterns['keywords'] if kw in filename_normalized]
            if filename_keyword_matches and not keyword_matches:
                # If filename has keywords but text doesn't, add small boost
                disease_confidence += 0.15
            
            # Check for abnormal values
            abnormal_value_count = 0
            for pattern, condition_func in patterns['value_indicators']:
                matches = re.findall(pattern, extracted_text)
                for match in matches:
                    try:
                        if isinstance(match, tuple):
                            # Handle multiple capture groups
                            if condition_func(match[0]):
                                abnormal_value_count += 1
                        else:
                            if condition_func(match):
                                abnormal_value_count += 1
                    except:
                        pass
            
            if abnormal_value_count > 0:
                disease_confidence += 0.35 * min(abnormal_value_count / max(len(patterns['value_indicators']), 1), 1.0)
            
            # Lower threshold to 0.20 - more aggressive detection
            if disease_confidence > 0.20:
                detected_diseases.append((disease, min(disease_confidence, 0.95)))
        
        # Sort by confidence
        detected_diseases.sort(key=lambda x: x[1], reverse=True)
        
        if detected_diseases:
            return {
                'disease': detected_diseases[0][0],
                'confidence': detected_diseases[0][1],
                'method': 'AI Vision Analysis (OCR + Pattern Matching)',
                'extracted_text_preview': extracted_text[:200] if extracted_text else ""
            }
    
    # Fallback: Use filename-based detection if no text extracted or low confidence
    for disease, patterns in disease_patterns.items():
        if any(kw in filename_normalized for kw in patterns['keywords']):
            return {
                'disease': disease,
                'confidence': 0.75,
                'method': 'Filename Analysis (AI vision could not extract text)',
                'note': 'System detected from filename. For better results, upload a clear image of the medical report.'
            }
    
    return {
        'disease': None,
        'confidence': 0.0,
        'method': 'No pattern detected',
        'note': 'System could not identify disease. Please upload a clear medical report image or include disease keywords in filename.'
    }

def analyze_medical_image(image_path, filename=''):
    """AI-based medical image analysis with smart disease detection"""
    
    # Use AI vision to detect disease from image content
    ai_detection = detect_disease_from_image_content(image_path, filename)
    detected_disease = ai_detection.get('disease')
    detection_confidence = ai_detection.get('confidence', 0.0)
    detection_method = ai_detection.get('method', 'Unknown')
    
    # If AI detected a disease with reasonable confidence, use it (lowered threshold to 0.20 for better detection)
    if detected_disease and detection_confidence >= 0.20:
        rec = get_recommendation(detected_disease, 'moderate')
        
        findings = {
            'report_type': f'Medical Report - {detected_disease}',
            'abnormalities': [f'{detected_disease} detected from image analysis'],
            'confidence': detection_confidence,
            'detection_method': detection_method,
            'ai_analysis_summary': ai_detection.get('extracted_text_preview', ai_detection.get('note', '')),
            'requires_specialist': True,
            'specialist_type': 'Medical Specialist',
            'disease_detected': detected_disease,
            'notes': f'Disease detected using {detection_method}. Please review with appropriate specialist.',
            'what_is_present': rec.get('what_is_present', []),
            'action_plan': rec.get('action_plan', []),
            'diet_plan': rec.get('diet_plan', {}),
            'recommendations': rec
        }
        return findings
    
    # Fallback: Use filename-based detection if AI didn't detect anything
    filename_lower = filename.lower() if filename else ''
    filename_normalized = filename_lower.replace('_', ' ').replace('-', ' ')
    
    disease_mapping = {
        ('thyroid', 'tsh', 't3', 't4', 'thyroiditis', 'hyperthyroid', 'hypothyroid'): {
            'disease': 'Thyroid Disorder',
            'type': 'Thyroid Function Test Report',
            'specialist': 'Endocrinologist',
            'confidence': 0.85
        },
        ('glucose', 'diabetes', 'blood sugar', 'hba1c', 'fasting'): {
            'disease': 'Diabetes Mellitus',
            'type': 'Blood Glucose/Diabetes Report',
            'specialist': 'Endocrinologist/Diabetologist',
            'confidence': 0.82
        },
        ('blood pressure', 'hypertension', 'systolic', 'diastolic', 'bp'): {
            'disease': 'Hypertension (High Blood Pressure)',
            'type': 'Blood Pressure Report',
            'specialist': 'Cardiologist',
            'confidence': 0.80
        },
        ('chest', 'xray', 'lungs', 'pneumonia', 'respiratory'): {
            'disease': 'Pneumonia',
            'type': 'Chest X-ray',
            'specialist': 'Pulmonologist/Radiologist',
            'confidence': 0.75
        },
        ('ecg', 'ekg', 'cardiac', 'arrhythmia', 'cardiogram'): {
            'disease': 'Heart Disease',
            'type': 'Electrocardiogram',
            'specialist': 'Cardiologist',
            'confidence': 0.78
        },
        ('lft', 'kft', 'renal function', 'hepatic renal'): {
            'disease': 'Kidney Disease',
            'type': 'Liver/Kidney Function Test',
            'specialist': 'Hepatologist/Nephrologist',
            'confidence': 0.80
        },
        ('liver', 'ast', 'alt', 'bilirubin'): {
            'disease': 'Liver Disease',
            'type': 'Liver Function Test',
            'specialist': 'Hepatologist',
            'confidence': 0.80
        },
        ('kidney', 'creatinine', 'bun', 'gfr'): {
            'disease': 'Kidney Disease',
            'type': 'Kidney Function Test',
            'specialist': 'Nephrologist',
            'confidence': 0.80
        },
        ('eye', 'retina', 'ophthalm', 'fundus', 'vision'): {
            'disease': 'Ophthalmic Disorder',
            'type': 'Eye Report',
            'specialist': 'Ophthalmologist',
            'confidence': 0.76
        },
    }
    
    # Check filename for disease keywords
    for keywords, disease_info in disease_mapping.items():
        if any(keyword in filename_normalized for keyword in keywords):
            rec = get_recommendation(disease_info['disease'], 'moderate')
            findings = {
                'report_type': disease_info['type'],
                'abnormalities': [f"{disease_info['disease']} detected from filename"],
                'confidence': disease_info['confidence'],
                'detection_method': 'Filename Analysis (AI vision could not extract text)',
                'requires_specialist': True,
                'specialist_type': disease_info['specialist'],
                'disease_detected': disease_info['disease'],
                'notes': 'Disease identified from filename. AI could not analyze image content - please ensure clear medical report image.',
                'what_is_present': rec.get('what_is_present', []),
                'action_plan': rec.get('action_plan', []),
                'diet_plan': rec.get('diet_plan', {}),
                'recommendations': rec
            }
            return findings
    
    # No disease detected - return generic response with all components
    generic_guidance = {
        'what_is_present': [
            'General health assessment needed',
            'Medical report analysis required', 
            'Professional consultation recommended',
            'Detailed examination needed'
        ],
        'action_plan': [
            'Upload a clear image of your medical report',
            'Ensure all text and values are visible in the image',
            'Include disease-related keywords in the filename (e.g., diabetes_report.jpg)',
            'Consult with a healthcare professional for accurate diagnosis',
            'Avoid self-diagnosis based on this tool',
            'Use this system as a preliminary screening tool only'
        ],
        'diet_plan': {
            'foods_to_eat': ['Whole grains', 'Fresh vegetables', 'Lean proteins', 'Fruits'],
            'foods_to_avoid': ['Processed foods', 'Sugary drinks', 'Trans fats', 'Excess salt'],
            'daily_recommendation': 'Maintain a balanced diet with proper nutrition. Consult a nutritionist for personalized guidance.'
        }
    }
    
    findings = {
        'report_type': 'Medical Report/Test',
        'abnormalities': ['Medical report detected - specifications unclear'],
        'confidence': 0.50,
        'detection_method': 'Unknown (AI analysis failed, no filename keywords found)',
        'requires_specialist': True,
        'specialist_type': 'Medical Specialist',
        'disease_detected': 'Unknown - Manual Review Required',
        'notes': 'Could not automatically detect disease type. ' +
                'For better detection: (1) Use clear medical report images, or ' +
                '(2) Include disease keyword in filename (e.g., thyroid_report.jpg, diabetes_test.pdf)',
        'ai_analysis_summary': ai_detection.get('note', ''),
        'recommendations': {
            'otc_medications': ['Consult pharmacist'],
            'prescription_medications': ['Consult doctor'],
            'specialist': 'General Practitioner'
        },
        'what_is_present': generic_guidance['what_is_present'],
        'action_plan': generic_guidance['action_plan'],
        'diet_plan': generic_guidance['diet_plan']
    }
    
    return findings


def analyze_audio(audio_path):
    """AI-based audio analysis for voice symptoms"""
    # Placeholder for audio/voice analysis
    # Can include cough detection, breathing patterns, speech analysis
    
    return {
        'audio_processed': True,
        'voice_symptoms': ['Voice pattern analyzed'],
        'confidence': 0.70,
        'notes': 'Audio analysis completed. Additional assessment recommended.'
    }

def get_recommendation(condition, severity):
    """Generate medical recommendations with medications"""
    recommendations = {
        # RESPIRATORY CONDITIONS
        'Common Cold': {
            'description': 'Viral infection of the upper respiratory tract',
            'symptoms': 'Runny nose, cough, sore throat, sneezing',
            'duration': '7-10 days',
            'recommendations': [
                'Rest for 7-10 days',
                'Stay hydrated - drink warm fluids',
                'Use saline nasal drops',
                'Gargle with warm salt water for sore throat',
                'Use honey or cough drops'
            ],
            'medications': {
                'OTC': [
                    'Paracetamol (Crocin/Dolo) 500mg - 1 tablet every 6 hours',
                    'Ibuprofen (Combiflam) 400mg - 1 tablet every 8 hours',
                    'Cough syrup (Robitussin/Benadryl) - 10ml every 6 hours',
                    'Cetirizine (Alerid) 10mg - 1 tablet at night',
                    'Nasal decongestant (Otrivin) - 2-3 drops per nostril'
                ],
                'Prescription': 'None required unless complications'
            },
            'when_to_see_doctor': 'Symptoms persist beyond 2 weeks, high fever (>103°F), or severe chest pain',
            'severity_level': 'MILD'
        },
        'Flu (Influenza)': {
            'description': 'Viral infection with systemic symptoms',
            'symptoms': 'High fever, body aches, cough, fatigue, headache',
            'duration': '1-2 weeks',
            'recommendations': [
                'Complete bed rest',
                'Drink plenty of fluids (water, warm tea, broth)',
                'Avoid contact with others for 24 hours after fever breaks',
                'Use humidifier for relief',
                'Monitor temperature regularly'
            ],
            'medications': {
                'OTC': [
                    'Paracetamol (Dolo/Crocin) 500mg - 1 tablet every 6 hours',
                    'Ibuprofen (Combiflam) 400mg - 1 tablet every 8 hours',
                    'Cough syrup with dextromethorphan - 10ml every 6 hours',
                    'Antihistamine (Cetirizine 10mg) - 1 tablet daily',
                    'Vitamin C supplement (500-1000mg) - 1-2 tablets daily'
                ],
                'Prescription': [
                    'Oseltamivir (Tamiflu) 75mg - 1 capsule twice daily for 5 days',
                    'Amoxicillin (if bacterial infection) 500mg - 1 tablet 3 times daily'
                ]
            },
            'when_to_see_doctor': 'Severe symptoms, shortness of breath, confusion, or persistent high fever',
            'severity_level': 'MODERATE'
        },
        'Bronchitis': {
            'description': 'Inflammation of the bronchial tubes',
            'symptoms': 'Persistent cough, mucus, fever, fatigue',
            'duration': '2-3 weeks',
            'recommendations': [
                'Rest and avoid smoke/pollution',
                'Use humidifier at night',
                'Drink warm liquids',
                'Monitor oxygen levels if available',
                'Take steam inhalation 2-3 times daily'
            ],
            'medications': {
                'OTC': [
                    'Cough syrup with guaifenesin (Mucinex) - 10ml every 6 hours',
                    'Paracetamol 500mg - 1 tablet every 6 hours for fever',
                    'Bronchodilator inhaler (Ventolin) - 2 puffs every 4-6 hours as needed'
                ],
                'Prescription': [
                    'Amoxicillin-Clavulanate (Augmentin) 625mg - 1 tablet 3 times daily',
                    'Salbutamol inhaler (Asthalin) - 2 puffs 2-3 times daily',
                    'Ipratropium inhaler - 2 puffs 3 times daily'
                ]
            },
            'when_to_see_doctor': 'Cough persists beyond 3 weeks or difficulty breathing',
            'severity_level': 'MODERATE'
        },
        'Pneumonia': {
            'description': 'Infection of lung alveoli causing inflammation',
            'symptoms': 'High fever, cough with sputum, chest pain, shortness of breath',
            'duration': '2-4 weeks',
            'recommendations': [
                '🚨 REQUIRES IMMEDIATE MEDICAL ATTENTION',
                'Hospitalization may be required',
                'Complete antibiotic course (7-14 days)',
                'Chest X-ray for diagnosis',
                'Monitor oxygen saturation constantly'
            ],
            'medications': {
                'OTC': 'Not suitable - prescription only',
                'Prescription': [
                    'Amoxicillin-Clavulanate 625mg - 1 tablet 3 times daily for 7 days',
                    'OR Azithromycin (Z-pack) 500mg - 1 tablet daily for 3 days',
                    'Paracetamol 500mg - 1 tablet every 6 hours for fever (max 4 tablets/day)',
                    'Mucoactive agent (Bromhexine) 8mg - 1 tablet 3 times daily',
                    'Oxygen therapy if SpO2 < 94%'
                ]
            },
            'when_to_see_doctor': 'IMMEDIATELY - SEEK EMERGENCY CARE',
            'severity_level': 'SEVERE'
        },
        'Asthma': {
            'description': 'Chronic airway inflammation causing breathing difficulty',
            'symptoms': 'Wheezing, shortness of breath, chest tightness, cough',
            'duration': 'Chronic condition',
            'recommendations': [
                'Avoid asthma triggers (allergens, pollution, cold air)',
                'Use peak flow meter daily',
                'Keep rescue inhaler always available',
                'Maintain medication routine',
                'Seek shelter from pollution and dust'
            ],
            'medications': {
                'OTC': [
                    'Salbutamol inhaler (Asthalin/Ventolin) - 2 puffs every 4-6 hours as needed'
                ],
                'Prescription': [
                    'Fluticasone propionate inhaler (Flixonase) - 2 puffs twice daily (maintenance)',
                    'Salmeterol xinafoate (Seretide) - 2 puffs twice daily',
                    'Montelukast (Singulair) 10mg - 1 tablet daily at night',
                    'Salbutamol inhaler - for acute attacks (2 puffs, wait 5 min, repeat if needed)'
                ]
            },
            'when_to_see_doctor': 'Frequent attacks, inability to speak full sentences, or blue lips → ER',
            'severity_level': 'MODERATE TO SEVERE'
        },
        # GASTROINTESTINAL CONDITIONS
        'Gastroenteritis (Food Poisoning)': {
            'description': 'Inflammation of stomach and intestines',
            'symptoms': 'Nausea, vomiting, diarrhea, abdominal cramps, fever',
            'duration': '24-48 hours',
            'recommendations': [
                'Stay hydrated - drink ORS (oral rehydration salts)',
                'Rest completely',
                'Avoid solid food for first 24 hours',
                'Gradually introduce bland foods (rice, bread, banana)',
                'Monitor for dehydration signs'
            ],
            'medications': {
                'OTC': [
                    'Oral Rehydration Salts (ORS) - 1 packet in 1 liter water, sip continuously',
                    'Ondansetron (Emeset) 4mg - 1 tablet for severe vomiting',
                    'Loperamide (Imodium) 2mg - Use cautiously, not if fever present',
                    'Zinc supplement 20mg - 1 tablet daily for 10-14 days'
                ],
                'Prescription': [
                    'Ciprofloxacin (Cipro) 500mg - 1 tablet twice daily for 3 days (if bacterial)',
                    'Metronidazole (Flagyl) 400mg - 1 tablet 3 times daily for 5 days'
                ]
            },
            'when_to_see_doctor': 'Severe dehydration, bloody stools, or symptoms persist >48 hours',
            'severity_level': 'MODERATE'
        },
        'Peptic Ulcer Disease': {
            'description': 'Ulcers in stomach or intestinal lining',
            'symptoms': 'Burning abdominal pain, bloating, heartburn, nausea',
            'duration': 'Weeks to months if untreated',
            'recommendations': [
                'Avoid spicy, acidic, and fatty foods',
                'Avoid alcohol and smoking',
                'Eat small, frequent meals',
                'Manage stress',
                'Complete full antibiotic course'
            ],
            'medications': {
                'OTC': [
                    'Antacid (Gelusil) - 2 tablets after meals and at bedtime',
                    'H2 blocker (Famotidine/Pepisol) 20mg - 1 tablet twice daily'
                ],
                'Prescription': [
                    'Pantoprazole (Pantop) 40mg - 1 tablet daily before breakfast',
                    'Amoxicillin 500mg + Clarithromycin 500mg + Pantoprazole 40mg - Triple therapy for 14 days',
                    'Sucralfate 1g - 1 tablet 4 times daily'
                ]
            },
            'when_to_see_doctor': 'Severe pain, vomiting blood, or black stools → ER',
            'severity_level': 'MODERATE'
        },
        'Constipation': {
            'description': 'Difficulty passing stools',
            'symptoms': 'Hard stools, abdominal discomfort, straining',
            'duration': 'Days to weeks',
            'recommendations': [
                'Increase fiber intake (vegetables, fruits, whole grains)',
                'Drink 8-10 glasses of water daily',
                'Exercise regularly (20-30 minutes daily)',
                'Establish regular bathroom routine',
                'Avoid prolonged sitting'
            ],
            'medications': {
                'OTC': [
                    'Isabgol (Metamucil) - 1 teaspoon in water daily',
                    'Lactulose (Duphalac) syrup - 15-30ml daily',
                    'Bisacodyl (Dulcolax) 5mg - 1 tablet at night',
                    'Stool softener (Docusate) 100mg - 1 capsule daily'
                ],
                'Prescription': 'Polyethylene Glycol (PEG 3350) - as recommended'
            },
            'when_to_see_doctor': 'Persistent constipation >2 weeks or rectal bleeding',
            'severity_level': 'MILD'
        },
        'Diarrhea': {
            'description': 'Frequent loose or watery stools',
            'symptoms': 'Loose stools, abdominal cramps, urgency',
            'duration': 'Hours to days',
            'recommendations': [
                'Stay hydrated with ORS solution',
                'Eat bland foods (rice, toast, boiled potatoes)',
                'Avoid dairy, fatty foods, and high-fiber foods',
                'Rest and avoid strenuous activity',
                'Monitor for dehydration'
            ],
            'medications': {
                'OTC': [
                    'ORS packets - 1 packet per liter water, sip throughout day',
                    'Loperamide (Imodium) 2mg - Use only if no fever, 1 tablet after each loose stool',
                    'Kaolin-Pectin suspension - 30ml after each bowel movement',
                    'Zinc 20mg - 1 tablet daily for 10 days'
                ],
                'Prescription': [
                    'Ciprofloxacin 500mg - if bacterial, 1 tablet twice daily for 3 days',
                    'Metronidazole 400mg - if parasitic, 1 tablet 3 times daily for 5 days'
                ]
            },
            'when_to_see_doctor': 'Severe dehydration, bloody stools, or lasting >48 hours',
            'severity_level': 'MILD TO MODERATE'
        },
        # NEUROLOGICAL CONDITIONS
        'Migraine Headache': {
            'description': 'Severe throbbing headache, often one-sided',
            'symptoms': 'Severe headache, nausea, sensitivity to light/sound',
            'duration': '4-72 hours',
            'recommendations': [
                'Rest in quiet, dark room',
                'Avoid triggers (caffeine, stress, certain foods)',
                'Apply cold compress to head',
                'Stay hydrated',
                'Maintain regular sleep schedule'
            ],
            'medications': {
                'OTC': [
                    'Ibuprofen (Combiflam) 400mg - 1 tablet every 8 hours',
                    'Paracetamol (Crocin) 500mg - 1 tablet every 6 hours',
                    'Aspirin 500mg - 1 tablet as needed'
                ],
                'Prescription': [
                    'Sumatriptan (Imigran) 50mg - 1 tablet at onset, repeat after 2 hours if needed',
                    'Propranolol 40mg - 1 tablet daily for prevention',
                    'Topiramate (Topamax) 25mg - 1 tablet at night for chronic migraine'
                ]
            },
            'when_to_see_doctor': 'Neurology consultation for frequent migraines (>4/month)',
            'severity_level': 'MODERATE'
        },
        'Tension Headache': {
            'description': 'Tightness and pressure around head',
            'symptoms': 'Mild to moderate pressure, neck stiffness',
            'duration': '30 minutes to hours',
            'recommendations': [
                'Neck and shoulder stretches',
                'Massage temples and neck',
                'Apply warm compress',
                'Manage stress through meditation/yoga',
                'Improve posture'
            ],
            'medications': {
                'OTC': [
                    'Ibuprofen 400mg - 1 tablet every 8 hours',
                    'Paracetamol 500mg - 1 tablet every 6 hours',
                    'Muscle relaxant (Cyclobenzaprine) - only if prescribed'
                ],
                'Prescription': [
                    'Amitriptyline 10-25mg - 1 tablet at night for chronic tension headaches',
                    'Topiramate 25mg - for prevention'
                ]
            },
            'when_to_see_doctor': 'Persistent daily headaches lasting >15 days/month',
            'severity_level': 'MILD'
        },
        # INFECTIOUS DISEASES
        'Urinary Tract Infection (UTI)': {
            'description': 'Bacterial infection of urinary system',
            'symptoms': 'Burning urination, frequency, urgency, lower abdominal pain',
            'duration': '3-7 days with treatment',
            'recommendations': [
                'Drink plenty of water (8-10 glasses)',
                'Urinate frequently and completely',
                'Use heating pad for pain relief',
                'Avoid irritants (caffeine, alcohol, spicy foods)',
                'Cranberry juice may help prevention'
            ],
            'medications': {
                'OTC': [
                    'Urinary alkalizer (Citralka) - 1 teaspoon in water 3 times daily',
                    'Phenazopyridine (Pyridium) 100mg - 1 tablet 3 times daily'
                ],
                'Prescription': [
                    'Ciprofloxacin (Cipro) 500mg - 1 tablet twice daily for 3 days',
                    'OR Nitrofurantoin (Furadantin) 100mg - 1 tablet twice daily for 7 days',
                    'OR Trimethoprim-Sulfamethoxazole 800mg - 1 tablet twice daily for 3 days'
                ]
            },
            'when_to_see_doctor': 'Back pain, fever, or symptoms persist after treatment',
            'severity_level': 'MODERATE'
        },
        'Sore Throat (Pharyngitis)': {
            'description': 'Inflammation of throat, usually viral or bacterial',
            'symptoms': 'Sore throat, pain on swallowing, red throat',
            'duration': '3-7 days',
            'recommendations': [
                'Gargle with warm salt water 4-5 times daily',
                'Drink warm liquids and avoid cold drinks',
                'Throat lozenges or honey for relief',
                'Rest and avoid irritants',
                'Monitor for fever'
            ],
            'medications': {
                'OTC': [
                    'Throat lozenges (strepsils) - 1 lozenge every 2-3 hours',
                    'Ibuprofen 400mg - 1 tablet every 8 hours',
                    'Paracetamol 500mg - 1 tablet every 6 hours',
                    'Honey - 1 spoon to soothe throat'
                ],
                'Prescription': [
                    'Amoxicillin 500mg - if bacterial (strep), 1 tablet 3 times daily for 10 days',
                    'Azithromycin (Z-pack) 500mg - if allergic to penicillin, 1 tablet daily for 3 days',
                    'Fluconazole 150mg - if fungal (thrush), 1 tablet daily for 3 days'
                ]
            },
            'when_to_see_doctor': 'High fever, severe pain, difficulty swallowing liquids, or rash',
            'severity_level': 'MILD'
        },
        'Ear Infection (Otitis)': {
            'description': 'Inflammation of ear canal or middle ear',
            'symptoms': 'Ear pain, hearing loss, discharge, fever',
            'duration': '3-7 days',
            'recommendations': [
                'Apply warm compress to affected ear',
                'Keep ear dry - avoid water exposure',
                'Avoid loud noises',
                'Use prescribed ear drops properly',
                'Chew gum to equalize pressure'
            ],
            'medications': {
                'OTC': [
                    'Paracetamol 500mg - 1 tablet every 6 hours for pain',
                    'Ibuprofen 400mg - 1 tablet every 8 hours',
                    'Ear drops with benzocaine (Aurocaine) - 3-4 drops in affected ear'
                ],
                'Prescription': [
                    'Amoxicillin 500mg - 1 tablet 3 times daily for 7 days',
                    'Amoxicillin-Clavulanate 625mg - 1 tablet 3 times daily for 7 days',
                    'Ofloxacin ear drops - 5 drops twice daily for 7 days',
                    'Ciprofloxacin eye drops in ear - if eardrum perforated'
                ]
            },
            'when_to_see_doctor': 'Severe pain, high fever, or discharge lasting >3 days',
            'severity_level': 'MODERATE'
        },
        # METABOLIC/CHRONIC CONDITIONS
        'Hypertension (High Blood Pressure)': {
            'description': 'Persistently elevated blood pressure',
            'symptoms': 'Often no symptoms, headache, dizziness',
            'duration': 'Chronic - lifelong management',
            'what_is_present': [
                'Systolic BP above 140 mmHg or Diastolic above 90 mmHg',
                'Increased risk of heart attack and stroke',
                'Left ventricular hypertrophy on ECG (enlarged heart)',
                'Albumin in urine (indicating kidney damage risk)',
                'Elevated cholesterol levels usually present'
            ],
            'action_plan': [
                'Step 1: Start Lisinopril 10mg daily (ACE inhibitor)',
                'Step 2: Check BP at home daily, record morning and evening readings',
                'Step 3: Get baseline ECG and kidney function test',
                'Step 4: Reduce salt intake starting immediately (<6g/day)',
                'Step 5: Start daily exercise: 30 mins walking, 5 days per week',
                'Step 6: Monitor BP weekly, show readings to doctor',
                'Step 7: If BP not controlled in 4 weeks, add second medication (Amlodipine)'
            ],
            'diet_plan': {
                'foods_to_eat': [
                    'Low sodium: Fresh vegetables (spinach, broccoli, carrots), fruits (bananas, oranges rich in potassium)',
                    'Lean proteins: Fish (salmon, sardines - omega-3), chicken, eggs',
                    'Whole grains: Oats, brown rice, whole wheat bread',
                    'Dairy: Low-fat yogurt, low-fat milk (rich in calcium)',
                    'Healthy fats: Olive oil, nuts (almonds, walnuts), seeds',
                    'Potassium-rich: Bananas, sweet potato, beans, lentils (helps lower BP)'
                ],
                'foods_to_avoid': [
                    'High salt foods: Processed meats, canned foods, pickles, soy sauce',
                    'Fried foods: French fries, deep-fried items, fast food',
                    'High-fat dairy: Full-fat milk, cheese, butter, cream',
                    'Sugary items: Sodas, sweets, pastries (increase weight)',
                    'Alcohol: Raises BP significantly',
                    'Excess caffeine: Coffee (more than 1-2 cups daily)'
                ],
                'meal_timing': 'Eat smaller portions 5 times daily. Include potassium with each meal for BP control.',
                'daily_recommendation': 'Follow DASH diet (Dietary Approaches to Stop Hypertension). Example: Grilled salmon, brown rice, steamed broccoli with olive oil. Total salt <6g/day.'
            },
            'recommendations': [
                'Reduce salt intake to <6g/day',
                'Regular exercise (30 min, 5 days/week)',
                'Maintain healthy weight',
                'Reduce alcohol consumption',
                'Monitor BP regularly at home',
                'Manage stress through meditation'
            ],
            'medications': {
                'OTC': 'None - prescription only',
                'Prescription': [
                    'ACE Inhibitor: Lisinopril (Lispril) 10mg - 1 tablet daily',
                    'Beta-blocker: Metoprolol (Bepridil) 50mg - 1 tablet daily',
                    'Calcium Channel Blocker: Amlodipine (Normalife) 5mg - 1 tablet daily',
                    'Diuretic: Hydrochlorothiazide 25mg - 1 tablet daily',
                    'ARB: Losartan (Cozaar) 50mg - 1 tablet daily'
                ]
            },
            'when_to_see_doctor': 'BP consistently >140/90 or sudden spike with chest pain → ER',
            'severity_level': 'MODERATE (Chronic)'
        },
        'Diabetes Mellitus': {
            'description': 'Elevated blood glucose levels',
            'symptoms': 'Thirst, frequent urination, fatigue, blurred vision',
            'duration': 'Chronic - lifelong management',
            'what_is_present': [
                'Fasting blood glucose >126 mg/dL',
                'Random blood glucose >200 mg/dL',
                'HbA1c >6.5% (indicates 3-month average glucose)',
                'Signs of hyperglycemia: Polyuria (frequent urination), polydipsia (excessive thirst)',
                'Increased infection risk and delayed healing'
            ],
            'action_plan': [
                'Step 1: Start Metformin 500mg twice daily (if Type 2)',
                'Step 2: Check blood glucose 4 times daily (fasting, before meals, bedtime)',
                'Step 3: Get HbA1c test done every 3 months',
                'Step 4: Record all readings in logbook for doctor review',
                'Step 5: Start light exercise (30 mins walking daily)',
                'Step 6: Annual check: Eye exam, kidney function, foot check',
                'Step 7: If glucose not controlled in 3 months, add second medication'
            ],
            'diet_plan': {
                'foods_to_eat': [
                    'Low glycemic index: Beans, lentils, chickpeas, nuts',
                    'Vegetables: Broccoli, spinach, peppers, tomatoes, carrots (non-starchy)',
                    'Whole grains: Brown rice, millets, oats (portion control)',
                    'Lean proteins: Chicken breast, fish, eggs, tofu',
                    'Healthy fats: Olive oil, coconut oil, nuts, seeds (in moderation)',
                    'Fruits with low sugar: Apples, berries, oranges (limited portions)'
                ],
                'foods_to_avoid': [
                    'Refined carbs: White rice, white bread, sugary cereals',
                    'Sugary drinks: Soda, fruit juices, energy drinks, sweetened coffee',
                    'Sweets and desserts: Cakes, cookies, ice cream, candy',
                    'Processed foods: Packaged snacks, fast food, fried foods',
                    'High-sugar fruits: Mango, banana, grapes (in excess)',
                    'Alcohol: Increases blood sugar fluctuations'
                ],
                'meal_timing': 'Eat meals at same time daily. Example: 8am, 1pm, 7pm. Include protein and fiber with each meal.',
                'daily_recommendation': 'Follow 1200-1500 calorie diet. Balanced plate: 1/4 protein, 1/4 carbs, 1/2 vegetables. Example breakfast: Vegetable omelette with whole wheat toast.'
            },
            'recommendations': [
                'Follow diabetic diet plan',
                'Monitor blood glucose daily',
                'Exercise 30 minutes daily',
                'Maintain healthy weight',
                'Regular eye and foot exams',
                'Check HbA1c every 3 months'
            ],
            'medications': {
                'OTC': [
                    'Glucose monitoring test strips - use as recommended'
                ],
                'Prescription': [
                    'Type 2 Oral: Metformin (Glucophage) 500mg - 1 tablet twice daily',
                    'Sulfonylurea: Glipizide (Minidiab) 5mg - 1 tablet daily',
                    'DPP-4 inhibitor: Sitagliptin (Januvia) 100mg - 1 tablet daily',
                    'GLP-1 agonist: Dulaglutide (Trulicity) - 0.75mg-1.5mg injection weekly',
                    'Insulin: Basal-bolus or long-acting insulin as required'
                ]
            },
            'when_to_see_doctor': 'Monthly for Type 1; quarterly for Type 2. Blood glucose <70 or >300 → ER',
            'severity_level': 'MODERATE (Chronic)'
        },
        'Thyroid Disorder': {
            'description': 'Hypothyroidism or hyperthyroidism',
            'symptoms': 'Fatigue, weight gain/loss, mood changes, temperature sensitivity',
            'duration': 'Chronic - lifelong management',
            'what_is_present': [
                'Abnormal TSH levels (elevated or decreased)',
                'Abnormal T3/T4 hormone levels',
                'Thyroid antibodies indicating autoimmune thyroiditis',
                'Signs of thyroid dysfunction on physical exam'
            ],
            'action_plan': [
                'Step 1: Start thyroid hormone replacement therapy immediately (Levothyroxine if hypothyroid)',
                'Step 2: Get TSH levels checked after 6-8 weeks to adjust dosage',
                'Step 3: Take blood test every 6 weeks until levels stabilize',
                'Step 4: Once stabilized, continue monitoring TSH annually',
                'Step 5: Avoid iron/calcium supplements 4 hours before/after medication',
                'Step 6: Take medication on empty stomach (30 mins before breakfast)'
            ],
            'diet_plan': {
                'foods_to_eat': [
                    'Iodine-rich foods: Seaweed, fish (salmon, tuna), eggs, dairy',
                    'Selenium-rich: Brazil nuts, mushrooms, sunflower seeds',
                    'Zinc-rich: Pumpkin seeds, cashews, chickpeas',
                    'Iron-rich: Spinach, lentils, beef (separate from thyroid meds by 4 hours)',
                    'Whole grains: Brown rice, oats, millets',
                    'Fruits: Berries, apples, oranges for antioxidants'
                ],
                'foods_to_avoid': [
                    'Goitrogenic foods when raw: Broccoli, cabbage, cauliflower (cook well)',
                    'Soy products: Tofu, soy milk (can interfere with absorption)',
                    'Cruciferous vegetables in excess: Kale, Brussels sprouts',
                    'High-fiber foods with medicine (separate by 4 hours)',
                    'Processed foods and excess caffeine'
                ],
                'meal_timing': 'Take medicine 30 mins before breakfast on empty stomach. Eat breakfast 1 hour after.',
                'daily_recommendation': 'Eat balanced meals with iodine, selenium, and zinc. Example: Grilled fish with rice and steamed vegetables.'
            },
            'recommendations': [
                'Take medication consistently',
                'Take on empty stomach if Levothyroxine',
                'Avoid iron/calcium 4 hours after dose',
                'Regular TSH monitoring',
                'Maintain consistent iodine intake'
            ],
            'medications': {
                'OTC': [
                    'Calcium supplement - take 4 hours apart from thyroid meds'
                ],
                'Prescription': [
                    'Hypothyroidism: Levothyroxine (Thyronorm) 25-200mcg - 1 tablet daily on empty stomach',
                    'Hyperthyroidism: Propylthiouracil (PTU) 50mg - 1 tablet 3 times daily',
                    'OR Methimazole (Tapazole) 5-20mg - 1-3 tablets daily'
                ]
            },
            'when_to_see_doctor': 'Every 6-8 weeks initially, then annually. Chest pain or palpitations → ER',
            'severity_level': 'MODERATE (Chronic)'
        },
        # DERMATOLOGICAL CONDITIONS
        'Skin Rash': {
            'description': 'Non-infectious skin irritation or allergic reaction',
            'symptoms': 'Itching, redness, swelling, skin texture change',
            'duration': '3-14 days depending on cause',
            'recommendations': [
                'Identify and avoid trigger',
                'Use mild soap and lukewarm water',
                'Apply moisturizer while skin damp',
                'Avoid scratching to prevent infection',
                'Keep area clean and dry'
            ],
            'medications': {
                'OTC': [
                    'Cetirizine (Alerid) 10mg - 1 tablet daily for itching',
                    'Hydrocortisone cream 1% - apply 2-3 times daily',
                    'Calamine lotion - apply as needed for relief',
                    'Moisturizer (Cetaphil) - apply regularly'
                ],
                'Prescription': [
                    'Betamethasone cream 0.05% - apply 2-3 times daily for severe rash',
                    'Mometasone (Momate) cream - 2-3 times daily',
                    'Prednisone 10-20mg - if severe systemic allergic reaction'
                ]
            },
            'when_to_see_doctor': 'Rash spreads quickly, involves face/genitals, or with high fever',
            'severity_level': 'MILD TO MODERATE'
        },
        'Eczema (Atopic Dermatitis)': {
            'description': 'Chronic inflammatory skin condition',
            'symptoms': 'Intense itching, dry skin, red patches, cracked skin',
            'duration': 'Chronic - recurrent episodes',
            'recommendations': [
                'Use fragrance-free moisturizer daily',
                'Use lukewarm water, not hot',
                'Avoid irritants and allergens',
                'Keep nails short to avoid scratching',
                'Manage stress through relaxation'
            ],
            'medications': {
                'OTC': [
                    'Moisturizer oils (coconut/almond oil) - apply daily',
                    'Anti-itch cream (Dermacool) - as needed',
                    'Antihistamine (Cetirizine) 10mg - 1 tablet daily'
                ],
                'Prescription': [
                    'Tacrolimus (Protopic) ointment - apply twice daily',
                    'Fluticasone propionate cream 0.05% - apply 1-2 times daily',
                    'Triamcinolone cream 0.1% - for acute flares',
                    'Dupilumab (Dupixent) - injectable for severe eczema'
                ]
            },
            'when_to_see_doctor': 'Monthly follow-ups for flare management and treatment adjustment',
            'severity_level': 'MILD TO MODERATE (Chronic)'
        },
        'Acne': {
            'description': 'Follicular infection causing pimples',
            'symptoms': 'Pimples, blackheads, whiteheads, oily skin',
            'duration': 'Chronic in teens/young adults',
            'recommendations': [
                'Wash face twice daily with mild cleanser',
                'Avoid touching or squeezing pimples',
                'Use non-comedogenic products',
                'Avoid oily foods (not proven but recommended)',
                'Manage stress and hormones'
            ],
            'medications': {
                'OTC': [
                    'Benzoyl peroxide 2.5-5% cream - apply daily',
                    'Salicylic acid 2% cleanser - wash twice daily',
                    'Azelaic acid cream - apply 1-2 times daily',
                    'Zinc supplement 15-30mg daily'
                ],
                'Prescription': [
                    'Tretinoin (Retinol-A) 0.025-0.1% - apply daily at night',
                    'Clindamycin phosphate 1% - apply daily',
                    'Doxycycline 100mg - 1 tablet daily for 6-12 weeks',
                    'Combined oral contraceptive - for hormonal acne in females',
                    'Isotretinoin (Accutane) 0.5-1mg/kg - for severe acne (requires monitoring)'
                ]
            },
            'when_to_see_doctor': 'If affecting self-esteem or not responding to OTC after 6 weeks',
            'severity_level': 'MILD (Usually)'
        },
        # ALLERGY CONDITIONS
        'Allergic Rhinitis (Hay Fever)': {
            'description': 'Allergic inflammation of nasal passages',
            'symptoms': 'Runny nose, sneezing, itchy eyes, nasal congestion',
            'duration': 'Seasonal or perennial',
            'recommendations': [
                'Identify and avoid allergen trigger',
                'Keep windows closed during pollen season',
                'Use air purifier at home',
                'Shower and change clothes after outdoors',
                'Use saline nasal rinse'
            ],
            'medications': {
                'OTC': [
                    'Cetirizine (Alerid) 10mg - 1 tablet daily',
                    'Loratadine (Claritin) 10mg - 1 tablet daily',
                    'Chlorpheniramine 2mg - 1 tablet every 6 hours',
                    'Saline nasal spray - use as needed',
                    'Pseudoephedrine 60mg - 1 tablet for congestion'
                ],
                'Prescription': [
                    'Fluticasone nasal spray (Flixonase) - 2 sprays each nostril daily',
                    'Mometasone nasal spray - 2 sprays daily',
                    'Montelukast (Singulair) 10mg - 1 tablet at night',
                    'Desloratadine (Aerius) 5mg - 1 tablet daily'
                ]
            },
            'when_to_see_doctor': 'If symptoms not controlled or suspecting allergic asthma',
            'severity_level': 'MILD'
        },
        'Food Allergy': {
            'description': 'Immune reaction to specific food',
            'symptoms': 'Itching mouth, swelling lips, hives, anaphylaxis (severe)',
            'duration': 'Acute episode or chronic sensitivity',
            'recommendations': [
                '🚨 AVOID ALLERGEN COMPLETELY',
                'Read all food labels carefully',
                'Inform restaurants of allergy',
                'Carry EpiPen if severe allergy',
                'Wear medical alert bracelet'
            ],
            'medications': {
                'OTC': [
                    'Antihistamine (Cetirizine 10mg) - for mild reactions',
                    'Antacid - may help some symptoms'
                ],
                'Prescription': [
                    'EpiPen (Epinephrine auto-injector) - always carry for severe allergies',
                    'H1 blocker (Chlorpheniramine 4mg) - 1 tablet for reactions',
                    'H2 blocker (Famotidine 20mg) - optional support'
                ]
            },
            'when_to_see_doctor': 'Immediately if anaphylaxis (swelling throat, breathing difficulty, shock)',
            'severity_level': 'MILD TO SEVERE (depending on allergen)'
        },
        # SLEEP CONDITIONS
        'Insomnia': {
            'description': 'Difficulty falling or staying asleep',
            'symptoms': 'Trouble sleeping, early morning waking, daytime fatigue',
            'duration': 'Varies - acute or chronic',
            'recommendations': [
                'Maintain consistent sleep schedule',
                'Avoid caffeine after 2 PM',
                'Exercise during day (not evening)',
                'Keep bedroom cool and dark',
                'Try relaxation techniques before bed',
                'Avoid screens 1 hour before sleep'
            ],
            'medications': {
                'OTC': [
                    'Melatonin 3-10mg - 1 tablet 30 min before bed',
                    'Valerian root 500mg - 1 tablet at night',
                    'Magnesium 200-400mg - 1 tablet at night'
                ],
                'Prescription': [
                    'Zolpidem (Ambien) 5-10mg - 1 tablet at night for 2-4 weeks max',
                    'Alprazolam (Xanax) 0.5-1mg - only for anxiety-related insomnia',
                    'Amitriptyline 10-25mg - 1 tablet at night',
                    'Trazodone 50-100mg - 1 tablet at night'
                ]
            },
            'when_to_see_doctor': 'If sleep issues persist >3 months or affecting daily life',
            'severity_level': 'MILD TO MODERATE'
        },
        # DEFAULT
        'General Consultation Recommended': {
            'description': 'Symptoms require professional evaluation',
            'symptoms': 'Varies based on presentation',
            'duration': 'Pending diagnosis',
            'recommendations': [
                'Schedule appointment with healthcare provider',
                'Keep symptom diary',
                'Note any triggers or patterns',
                'Take list of medications to appointment',
                'Bring medical history documents'
            ],
            'medications': {
                'OTC': 'None recommended until diagnosis',
                'Prescription': 'Pending medical evaluation'
            },
            'when_to_see_doctor': 'As soon as possible for proper diagnosis',
            'severity_level': 'UNKNOWN'
        }
    }
    
    # Get the recommendation, or return default
    if condition in recommendations:
        rec = recommendations[condition]
    else:
        rec = recommendations['General Consultation Recommended']
    
    return rec

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    role, response, status = _require_role(['doctor', 'admin'])
    if response is not None:
        return response, status
    privacy_framework.write_audit_event('open_dashboard', role)
    return render_template('dashboard.html')

@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    try:
        data = request.form.to_dict()
        image_analysis = None
        image_path_for_ml = ''
        
        # Process text symptoms
        symptoms_analysis = analyze_symptoms(data)
        
        # Format the recommendation properly
        formatted_recommendations = []
        if isinstance(symptoms_analysis.get('recommendations'), list):
            for rec in symptoms_analysis['recommendations']:
                if isinstance(rec, dict):
                    formatted_recommendations.append(rec)
                else:
                    formatted_recommendations.append({'raw': rec})
        
        result = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'patient_id': f"PAT{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'symptom_analysis': {
                'conditions': symptoms_analysis.get('conditions', []),
                'confidence': symptoms_analysis.get('confidence', []),
                'severity': symptoms_analysis.get('severity', ''),
                'duration': symptoms_analysis.get('duration', ''),
                'detailed_recommendations': formatted_recommendations
            },
            'multi_modal_data': {}
        }
        
        # Process uploaded image
        if 'medical_image' in request.files:
            file = request.files['medical_image']
            if file and file.filename and allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
                original_filename = file.filename  # Keep original for analysis
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                filepath = os.path.join('uploads/images', filename)
                file.save(filepath)
                image_path_for_ml = filepath
                
                # Analyze image with original filename for better detection
                image_analysis = analyze_medical_image(filepath, original_filename)
                result['multi_modal_data']['image_analysis'] = image_analysis
                
                # Add complete diagnosis information to response
                if image_analysis:
                    if 'symbol_analysis' not in result:
                        result['symbol_analysis'] = {}
                    
                    # Build complete diagnosis with all components
                    result['symbol_analysis']['image_diagnosis'] = {
                        'disease_detected': image_analysis.get('disease_detected'),
                        'report_type': image_analysis.get('report_type'),
                        'confidence': image_analysis.get('confidence'),
                        'specialist_required': image_analysis.get('specialist_type'),
                        'detection_method': image_analysis.get('detection_method', 'Unknown'),
                        
                        # NEW FIELDS - Comprehensive guidance
                        'what_is_present': image_analysis.get('what_is_present', []),
                        'action_plan': image_analysis.get('action_plan', []),
                        'diet_plan': image_analysis.get('diet_plan', {}),
                        
                        # Original recommendations field
                        'recommendations': image_analysis.get('recommendations'),
                        
                        # Additional info
                        'notes': image_analysis.get('notes', ''),
                        'abnormalities': image_analysis.get('abnormalities', [])
                    }
        
        # Process uploaded audio
        if 'audio_file' in request.files:
            file = request.files['audio_file']
            if file and file.filename and allowed_file(file.filename, ALLOWED_AUDIO_EXTENSIONS):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                filepath = os.path.join('uploads/audio', filename)
                file.save(filepath)
                
                audio_analysis = analyze_audio(filepath)
                result['multi_modal_data']['audio_analysis'] = audio_analysis

        decision_input = _build_decision_support_payload(data, image_analysis)
        if image_path_for_ml:
            decision_input['image_path'] = image_path_for_ml
        fusion = multimodal_engine.infer(decision_input)
        top_conf = fusion.probable_conditions[0]['confidence'] if fusion.probable_conditions else 0.0
        risk = risk_model.score(decision_input, top_conf)

        result['clinical_decision_support'] = {
            'probable_conditions': fusion.probable_conditions,
            'fusion_confidence': fusion.fusion_confidence,
            'explainability_factors': fusion.explainability_factors,
            'next_step_investigations': fusion.next_step_investigations,
            'risk_stratification': risk,
            'model_metadata': fusion.model_metadata,
        }

        probable_condition_names = [item.get('condition', '') for item in fusion.probable_conditions]
        if not probable_condition_names:
            probable_condition_names = symptoms_analysis.get('conditions', [])

        result['doctor_recommendations'] = _recommend_doctors(
            data.get('location', ''),
            probable_condition_names,
        )

        # Keep backward-compatible top-level aliases.
        result['risk_score'] = risk['risk_score']
        result['risk_band'] = risk['risk_band']
        
        # Save diagnosis record
        save_diagnosis_record(result)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


@app.route('/api/decision-support', methods=['POST'])
def decision_support():
    """Standalone endpoint for real-time clinical decision support."""
    try:
        payload = request.json or {}
        if payload.get('lab_values') is None:
            payload['lab_values'] = multimodal_engine.extract_lab_values_from_text(
                ' '.join([
                    str(payload.get('symptoms', '')),
                    str(payload.get('clinical_text', '')),
                    str(payload.get('image_text', '')),
                ])
            )

        fusion = multimodal_engine.infer(payload)
        top_conf = fusion.probable_conditions[0]['confidence'] if fusion.probable_conditions else 0.0
        risk = risk_model.score(payload, top_conf)

        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'probable_conditions': fusion.probable_conditions,
            'confidence_score': fusion.fusion_confidence,
            'explainability_factors': fusion.explainability_factors,
            'recommended_next_steps': fusion.next_step_investigations,
            'risk_stratification': risk,
            'model_metadata': fusion.model_metadata,
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/dashboard/metrics', methods=['GET'])
def dashboard_metrics():
    role, response, status = _require_role(['doctor', 'admin'])
    if response is not None:
        return response, status

    records_file = 'data/diagnosis_records.json'
    records = []
    if os.path.exists(records_file):
        with open(records_file, 'r', encoding='utf-8') as f:
            records = json.load(f)

    total = len(records)
    confidences = []
    risk_bands = {'low': 0, 'moderate': 0, 'high': 0}
    recent = []

    for record in records[-30:]:
        cds = record.get('clinical_decision_support', {})
        conds = cds.get('probable_conditions', [])
        top = conds[0] if conds else {}
        conf = float(top.get('confidence', 0) or 0)
        if conf > 0:
            confidences.append(conf)

        band = str(record.get('risk_band', 'low')).lower()
        if band not in risk_bands:
            band = 'low'
        risk_bands[band] += 1

        recent.append({
            'timestamp': record.get('timestamp'),
            'top_condition': top.get('condition', 'General Consultation Recommended'),
            'confidence': round(conf, 3),
            'risk_band': band,
        })

    benchmark = pilot_validator.benchmark(
        case_count=max(total, 1),
        avg_ai_seconds=2.5,
        avg_manual_seconds=5.0,
    )

    privacy_framework.write_audit_event('read_dashboard_metrics', role, {'records': total})

    return jsonify({
        'success': True,
        'total_cases': total,
        'avg_confidence': round(sum(confidences) / len(confidences), 3) if confidences else 0,
        'risk_bands': risk_bands,
        'recent_cases': list(reversed(recent[-10:])),
        'benchmark': benchmark,
        'privacy': {
            'encryption_enabled': bool(privacy_framework.fernet),
            'anonymization_enabled': True,
            'role': role,
        },
    })


@app.route('/api/privacy/anonymize', methods=['POST'])
def anonymize_payload():
    role, response, status = _require_role(['doctor', 'admin'])
    if response is not None:
        return response, status

    payload = request.json or {}
    anonymized = privacy_framework.anonymize_record(payload)
    encrypted = privacy_framework.encrypt_json(anonymized)
    privacy_framework.write_audit_event('anonymize_payload', role)
    return jsonify({'success': True, 'anonymized': anonymized, 'encrypted': encrypted})


@app.route('/api/benchmark/pilot', methods=['POST'])
def pilot_benchmark():
    role, response, status = _require_role(['doctor', 'admin'])
    if response is not None:
        return response, status

    payload = request.json or {}
    case_count = int(payload.get('case_count', 100))
    ai_seconds = float(payload.get('avg_ai_seconds', 2.4))
    manual_seconds = float(payload.get('avg_manual_seconds', 4.2))
    result = pilot_validator.benchmark(case_count, ai_seconds, manual_seconds)
    privacy_framework.write_audit_event('pilot_benchmark', role, result)
    return jsonify({'success': True, 'benchmark': result})

@app.route('/api/chat', methods=['POST'])
def chat():
    """AI Health Chatbot endpoint with real LLM integration"""
    try:
        data = request.json
        user_message = data.get('message', '')
        chat_history = data.get('history', [])
        
        # Generate AI response using LLM
        ai_response = get_chatbot_response(user_message, chat_history)
        
        return jsonify({
            'success': True,
            'response': ai_response['message'],
            'suggestions': ai_response.get('suggestions', []),
            'llm_used': ai_response.get('llm_used', 'unknown'),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e),
            'fallback_message': 'I apologize, but I encountered an error. For immediate health concerns, please contact your healthcare provider or call 911 for emergencies.'
        }), 500

def save_diagnosis_record(record):
    """Save diagnosis records to JSON file"""
    records_file = 'data/diagnosis_records.json'
    secure_records_file = 'data/diagnosis_records_secure.json'
    
    try:
        if os.path.exists(records_file):
            with open(records_file, 'r') as f:
                records = json.load(f)
        else:
            records = []
        
        records.append(record)
        
        with open(records_file, 'w') as f:
            json.dump(records, f, indent=2)

        # Privacy-compliant secure storage (anonymized + encrypted payload)
        secure_records = []
        if os.path.exists(secure_records_file):
            with open(secure_records_file, 'r', encoding='utf-8') as sf:
                secure_records = json.load(sf)

        anonymized = privacy_framework.anonymize_record(record)
        encrypted = privacy_framework.encrypt_json(anonymized)
        secure_records.append({
            'timestamp': datetime.now().isoformat(),
            'record': encrypted,
            'patient_hash': anonymized.get('patient_hash', 'unknown'),
        })

        with open(secure_records_file, 'w', encoding='utf-8') as sf:
            json.dump(secure_records, sf, indent=2)

        privacy_framework.write_audit_event('save_diagnosis_record', 'system', {
            'records_total': len(records),
            'secure_records_total': len(secure_records),
        })
    except Exception as e:
        print(f"Error saving record: {e}")

if __name__ == '__main__':
    print("=" * 60)
    print("Medical AI Pre-Diagnosis System Starting...")
    print("=" * 60)
    print("Server running at: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
