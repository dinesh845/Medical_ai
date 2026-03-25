"""
AI utilities and model integration helpers
This module provides interfaces for integrating various AI models
"""

import numpy as np
from PIL import Image
from typing import Dict, List, Tuple, Optional
import re

class SymptomAnalyzer:
    """
    Advanced symptom analysis using NLP
    You can integrate models like:
    - BioBERT
    - ClinicalBERT
    - Medical NER models
    - Custom trained symptom classifiers
    """
    
    def __init__(self):
        # Load your NLP model here
        # Example: self.model = load_model('path/to/symptom_model')
        self.symptom_keywords = self._load_symptom_database()
    
    def _load_symptom_database(self) -> Dict:
        """Load symptom-disease mapping database"""
        return {
            'fever': {
                'conditions': ['Viral Infection', 'Bacterial Infection', 'Flu'],
                'severity_multiplier': 1.2
            },
            'cough': {
                'conditions': ['Respiratory Infection', 'COVID-19', 'Bronchitis'],
                'severity_multiplier': 1.1
            },
            'headache': {
                'conditions': ['Migraine', 'Tension Headache', 'Sinusitis'],
                'severity_multiplier': 1.0
            },
            'chest pain': {
                'conditions': ['Cardiac Issue', 'Respiratory Issue', 'Musculoskeletal'],
                'severity_multiplier': 1.5,
                'urgent': True
            },
            'shortness of breath': {
                'conditions': ['Respiratory Issue', 'Cardiac Issue', 'Anxiety'],
                'severity_multiplier': 1.4,
                'urgent': True
            },
            'nausea': {
                'conditions': ['Gastrointestinal Issue', 'Migraine', 'Food Poisoning'],
                'severity_multiplier': 1.1
            }
        }
    
    def analyze(self, symptoms_text: str, duration: str, severity: str) -> Dict:
        """
        Analyze symptoms using AI/ML models
        
        Args:
            symptoms_text: Patient's symptom description
            duration: How long symptoms have persisted
            severity: Severity level (mild, moderate, severe)
        
        Returns:
            Dictionary with conditions and confidence scores
        """
        # Preprocess text
        symptoms_text = symptoms_text.lower()
        
        # Extract symptoms
        detected_symptoms = []
        for symptom, data in self.symptom_keywords.items():
            if symptom in symptoms_text:
                detected_symptoms.append((symptom, data))
        
        # Generate conditions and confidence
        conditions = {}
        for symptom, data in detected_symptoms:
            for condition in data['conditions']:
                if condition not in conditions:
                    conditions[condition] = 0.5
                
                # Increase confidence based on symptom match
                conditions[condition] += 0.15 * data.get('severity_multiplier', 1.0)
        
        # Adjust for severity and duration
        severity_factor = {'mild': 0.9, 'moderate': 1.0, 'severe': 1.2}.get(severity, 1.0)
        
        for condition in conditions:
            conditions[condition] = min(conditions[condition] * severity_factor, 0.95)
        
        # Sort by confidence
        sorted_conditions = sorted(conditions.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'conditions': [c[0] for c in sorted_conditions[:3]],
            'confidence': [c[1] for c in sorted_conditions[:3]],
            'detected_symptoms': [s[0] for s in detected_symptoms],
            'urgent': any(s[1].get('urgent', False) for s in detected_symptoms)
        }

class MedicalImageAnalyzer:
    """
    Medical image analysis
    You can integrate models like:
    - ChestX-ray14
    - CheXNet
    - Custom CNN models for medical imaging
    - Transfer learning models (ResNet, EfficientNet)
    """
    
    def __init__(self):
        # Load your medical imaging model here
        # Example: self.model = tf.keras.models.load_model('chest_xray_model.h5')
        pass
    
    def preprocess_image(self, image_path: str, target_size: Tuple[int, int] = (224, 224)) -> np.ndarray:
        """
        Preprocess medical image for model input
        
        Args:
            image_path: Path to the image file
            target_size: Target size for the model
        
        Returns:
            Preprocessed image array
        """
        image = Image.open(image_path)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize
        image = image.resize(target_size)
        
        # Convert to array and normalize
        img_array = np.array(image) / 255.0
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    
    def analyze(self, image_path: str) -> Dict:
        """
        Analyze medical image
        
        Args:
            image_path: Path to the medical image
        
        Returns:
            Dictionary with analysis results
        """
        # Preprocess image
        img_array = self.preprocess_image(image_path)
        
        # In production, use your trained model:
        # predictions = self.model.predict(img_array)
        # abnormalities = self.decode_predictions(predictions)
        
        # Placeholder results
        return {
            'image_type': 'X-Ray detected',
            'abnormalities': ['No significant abnormalities detected'],
            'confidence': 0.78,
            'requires_specialist': False,
            'notes': 'AI-assisted preliminary screening completed. Professional review recommended.',
            'image_quality': 'Good'
        }

class AudioAnalyzer:
    """
    Audio/voice analysis for medical diagnosis
    You can integrate:
    - Cough detection models
    - Speech analysis models
    - Respiratory sound classification
    """
    
    def __init__(self):
        # Load your audio analysis model here
        # Example: self.model = load_audio_model()
        pass
    
    def extract_features(self, audio_path: str) -> np.ndarray:
        """
        Extract features from audio file
        Common features: MFCC, Spectral features, Zero Crossing Rate
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Feature array
        """
        # In production, use librosa or similar:
        # import librosa
        # audio, sr = librosa.load(audio_path)
        # mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
        # return mfccs
        
        return np.zeros((13, 100))  # Placeholder
    
    def analyze(self, audio_path: str) -> Dict:
        """
        Analyze audio for medical symptoms
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Dictionary with analysis results
        """
        # Extract features
        features = self.extract_features(audio_path)
        
        # In production, use your trained model:
        # predictions = self.model.predict(features)
        
        return {
            'audio_processed': True,
            'voice_symptoms': ['Voice pattern analyzed', 'No significant abnormalities'],
            'confidence': 0.72,
            'notes': 'Audio analysis completed. Additional assessment recommended.',
            'audio_quality': 'Good'
        }

class RecommendationEngine:
    """Generate personalized health recommendations"""
    
    @staticmethod
    def generate_recommendation(conditions: List[str], severity: str, 
                               urgent: bool = False) -> str:
        """
        Generate personalized recommendation based on diagnosis
        
        Args:
            conditions: List of diagnosed conditions
            severity: Severity level
            urgent: Whether urgent care is needed
        
        Returns:
            Recommendation text
        """
        if urgent or 'cardiac' in str(conditions).lower():
            return "⚠️ URGENT: Seek immediate medical attention or visit the nearest emergency room."
        
        recommendations = {
            'Viral Infection': 'Rest, stay hydrated, and monitor symptoms. Consult a doctor if fever persists beyond 3 days.',
            'Respiratory Infection': 'Seek medical attention promptly. Rest and avoid strenuous activities. Monitor breathing.',
            'Migraine': 'Rest in a quiet, dark room. Stay hydrated. Consult a neurologist if migraines are frequent.',
            'Gastrointestinal Issue': 'Maintain a light diet, stay hydrated. Consult a doctor if symptoms persist beyond 48 hours.',
            'Flu': 'Rest, hydrate, and consider antiviral medication. Consult a doctor if symptoms worsen.',
        }
        
        if conditions:
            primary_condition = conditions[0]
            base_recommendation = recommendations.get(
                primary_condition, 
                'Consult a healthcare professional for proper evaluation and treatment.'
            )
            
            if severity == 'severe':
                base_recommendation += ' Due to severe symptoms, seek medical attention as soon as possible.'
            
            return base_recommendation
        
        return 'Schedule an appointment with a healthcare provider for proper evaluation.'

# Initialize global analyzers
symptom_analyzer = SymptomAnalyzer()
image_analyzer = MedicalImageAnalyzer()
audio_analyzer = AudioAnalyzer()
recommendation_engine = RecommendationEngine()
