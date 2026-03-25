"""
Database models and data storage management
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class DiagnosisRecord:
    """Model for diagnosis records"""
    
    def __init__(self, patient_id: str, patient_name: str, age: int, 
                 gender: str, symptoms: str, diagnosis: Dict, timestamp: str):
        self.patient_id = patient_id
        self.patient_name = patient_name
        self.age = age
        self.gender = gender
        self.symptoms = symptoms
        self.diagnosis = diagnosis
        self.timestamp = timestamp
    
    def to_dict(self) -> Dict:
        """Convert record to dictionary"""
        return {
            'patient_id': self.patient_id,
            'patient_name': self.patient_name,
            'age': self.age,
            'gender': self.gender,
            'symptoms': self.symptoms,
            'diagnosis': self.diagnosis,
            'timestamp': self.timestamp
        }

class DataStorage:
    """Simple JSON-based data storage"""
    
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        self.records_file = os.path.join(data_dir, 'diagnosis_records.json')
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        os.makedirs(self.data_dir, exist_ok=True)
        if not os.path.exists(self.records_file):
            with open(self.records_file, 'w') as f:
                json.dump([], f)
    
    def save_record(self, record: DiagnosisRecord) -> bool:
        """Save a diagnosis record"""
        try:
            records = self.get_all_records()
            records.append(record.to_dict())
            
            with open(self.records_file, 'w') as f:
                json.dump(records, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving record: {e}")
            return False
    
    def get_all_records(self) -> List[Dict]:
        """Get all diagnosis records"""
        try:
            if os.path.exists(self.records_file):
                with open(self.records_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error reading records: {e}")
            return []
    
    def get_record_by_patient_id(self, patient_id: str) -> Optional[Dict]:
        """Get record by patient ID"""
        records = self.get_all_records()
        for record in records:
            if record.get('patient_id') == patient_id:
                return record
        return None
    
    def get_records_by_date(self, date: str) -> List[Dict]:
        """Get records by date"""
        records = self.get_all_records()
        return [r for r in records if r.get('timestamp', '').startswith(date)]
    
    def get_total_records(self) -> int:
        """Get total number of records"""
        return len(self.get_all_records())
    
    def delete_record(self, patient_id: str) -> bool:
        """Delete a record by patient ID"""
        try:
            records = self.get_all_records()
            filtered_records = [r for r in records if r.get('patient_id') != patient_id]
            
            with open(self.records_file, 'w') as f:
                json.dump(filtered_records, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error deleting record: {e}")
            return False

# Create global storage instance
storage = DataStorage()
