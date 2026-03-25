# 🏥 Medical AI System - USAGE EXAMPLES & TEST CASES

## How to Use the Complete System

Your Medical AI now has 25+ diseases with 50+ medications. Here's how to test and use it.

---

## 🚀 GETTING STARTED

### 1. Start the Flask Server
```bash
python app.py
```

Server will run at: **http://localhost:5000**

### 2. Access the Web Interface
Open browser and go to: `http://localhost:5000`

### 3. Use the API
Make POST requests to `/api/diagnose` endpoint

---

## 📋 TEST CASES WITH EXPECTED RESULTS

### **TEST 1: Common Cold** ❄️

**Input:**
```json
POST /api/diagnose
{
  "symptoms": "I have a cough, sore throat, and runny nose",
  "severity": "mild",
  "duration": "3 days"
}
```

**Expected Output:**
```json
{
  "success": true,
  "symptom_analysis": {
    "conditions": ["Common Cold", "Sore Throat (Pharyngitis)", ...],
    "confidence": [0.80, 0.70, ...],
    "severity": "mild",
    "detailed_recommendations": [
      {
        "description": "Viral infection of the upper respiratory tract",
        "symptoms": "Runny nose, cough, sore throat, sneezing",
        "medications": {
          "OTC": [
            "Paracetamol (Crocin/Dolo) 500mg - 1 tablet every 6 hours",
            "Ibuprofen (Combiflam) 400mg - 1 tablet every 8 hours",
            "Cough syrup (Robitussin/Benadryl) - 10ml every 6 hours",
            "Cetirizine (Alerid) 10mg - 1 tablet at night",
            "Nasal decongestant (Otrivin) - 2-3 drops per nostril"
          ],
          "Prescription": "None required unless complications"
        },
        "recommendations": [
          "Rest for 7-10 days",
          "Stay hydrated - drink warm fluids",
          "Use saline nasal drops",
          "Gargle with warm salt water for sore throat",
          "Use honey or cough drops"
        ],
        "when_to_see_doctor": "Symptoms persist beyond 2 weeks, high fever (>103°F), or severe chest pain",
        "severity_level": "MILD"
      }
    ]
  }
}
```

**Key Points**:
- ✅ Common Cold identified (80% confidence)
- ✅ 5 OTC medication options provided
- ✅ Exact dosages given (500mg, 400mg, 10ml)
- ✅ Frequency specified (every 6 hours, at night)
- ✅ Brand names included (Crocin, Dolo, Combiflam)
- ✅ When to see doctor guidance included

---

### **TEST 2: Flu/Influenza** 🤒

**Input:**
```json
POST /api/diagnose
{
  "symptoms": "fever, body ache, cough, and extreme fatigue",
  "severity": "moderate",
  "duration": "2 days"
}
```

**Expected Output:**
```json
{
  "success": true,
  "symptom_analysis": {
    "conditions": ["Flu (Influenza)", "Common Cold", "Viral Infection"],
    "confidence": [0.85, 0.72, 0.65],
    "detailed_recommendations": [
      {
        "description": "Viral infection with systemic symptoms",
        "symptoms": "High fever, body aches, cough, fatigue, headache",
        "duration": "1-2 weeks",
        "medications": {
          "OTC": [
            "Paracetamol (Dolo/Crocin) 500mg - 1 tablet every 6 hours",
            "Ibuprofen (Combiflam) 400mg - 1 tablet every 8 hours",
            "Cough syrup with dextromethorphan - 10ml every 6 hours",
            "Cetirizine (Alerid) 10mg - 1 tablet daily",
            "Vitamin C supplement (500-1000mg) - 1-2 tablets daily"
          ],
          "Prescription": [
            "Oseltamivir (Tamiflu) 75mg - 1 capsule twice daily for 5 days",
            "Amoxicillin 500mg - 1 tablet 3 times daily"
          ]
        },
        "recommendations": [
          "Complete bed rest",
          "Drink plenty of fluids (water, warm tea, broth)",
          "Avoid contact with others for 24 hours after fever breaks",
          "Use humidifier for relief",
          "Monitor temperature regularly"
        ],
        "when_to_see_doctor": "Severe symptoms, shortness of breath, confusion, or persistent high fever",
        "severity_level": "MODERATE"
      }
    ]
  }
}
```

**Key Points**:
- ✅ Flu identified with HIGH confidence (85%)
- ✅ 5 OTC options with specific dosages
- ✅ 2 Prescription options (Tamiflu, Amoxicillin)
- ✅ Complete recommendations provided
- ✅ Severity level: MODERATE
- ✅ Duration: 1-2 weeks

---

### **TEST 3: Emergency Case** 🚨

**Input:**
```json
POST /api/diagnose
{
  "symptoms": "I have severe chest pain and difficulty breathing",
  "severity": "critical",
  "duration": "1 hour"
}
```

**Expected Output:**
```json
{
  "success": true,
  "symptom_analysis": {
    "conditions": ["🚨 EMERGENCY - SEEK IMMEDIATE HELP 🚨"],
    "confidence": [1.0],
    "severity": "CRITICAL",
    "detailed_recommendations": [
      {
        "message": "🚨 **EMERGENCY DETECTED** 🚨\n\nPlease contact emergency services immediately:\n• Call 911 (USA)\n• Go to the nearest hospital\n• Contact your local emergency number",
        "severity": "CRITICAL",
        "suggestions": ["Call Emergency Services", "Go to Hospital", "Contact Doctor"]
      }
    ]
  }
}
```

**Key Points**:
- ✅ EMERGENCY DETECTION TRIGGERED
- ✅ Confidence: 100%
- ✅ Severity: CRITICAL
- ✅ Clear emergency instructions provided
- ✅ Visual alert with 🚨 emoji

---

### **TEST 4: Urinary Tract Infection (UTI)** 🏥

**Input:**
```json
POST /api/diagnose
{
  "symptoms": "burning sensation during urination, frequent urges to urinate, and lower abdominal pain",
  "severity": "moderate",
  "duration": "2 days"
}
```

**Expected Output:**
```json
{
  "success": true,
  "symptom_analysis": {
    "conditions": ["Urinary Tract Infection (UTI)", "General Consultation Recommended"],
    "confidence": [0.82, 0.50],
    "detailed_recommendations": [
      {
        "description": "Bacterial infection of urinary system",
        "symptoms": "Burning urination, frequency, urgency, lower abdominal pain",
        "duration": "3-7 days with treatment",
        "medications": {
          "OTC": [
            "Urinary alkalizer (Citralka) - 1 teaspoon in water 3 times daily",
            "Phenazopyridine (Pyridium) 100mg - 1 tablet 3 times daily"
          ],
          "Prescription": [
            "Ciprofloxacin (Cipro) 500mg - 1 tablet twice daily for 3 days",
            "OR Nitrofurantoin (Furadantin) 100mg - 1 tablet twice daily for 7 days",
            "OR Trimethoprim-Sulfamethoxazole 800mg - 1 tablet twice daily for 3 days"
          ]
        },
        "recommendations": [
          "Drink plenty of water (8-10 glasses)",
          "Urinate frequently and completely",
          "Use heating pad for pain relief",
          "Avoid irritants (caffeine, alcohol, spicy foods)",
          "Cranberry juice may help prevention"
        ],
        "when_to_see_doctor": "Back pain, fever, or symptoms persist after treatment",
        "severity_level": "MODERATE"
      }
    ]
  }
}
```

**Key Points**:
- ✅ UTI identified with very high confidence (82%)
- ✅ 2 OTC options provided
- ✅ 3 Prescription alternatives offered
- ✅ Complete treatment duration (3-7 days)
- ✅ Specific recommendations

---

### **TEST 5: Migraine Headache** 🧠

**Input:**
```json
POST /api/diagnose
{
  "symptoms": "severe headache on one side of head, nausea, sensitivity to light",
  "severity": "moderate",
  "duration": "4 hours"
}
```

**Expected Output:**
```json
{
  "success": true,
  "symptom_analysis": {
    "conditions": ["Migraine Headache", "Tension Headache"],
    "confidence": [0.75, 0.65],
    "detailed_recommendations": [
      {
        "description": "Severe throbbing headache, often one-sided",
        "symptoms": "Severe headache, nausea, sensitivity to light/sound",
        "duration": "4-72 hours",
        "medications": {
          "OTC": [
            "Ibuprofen (Combiflam) 400mg - 1 tablet every 8 hours",
            "Paracetamol (Crocin) 500mg - 1 tablet every 6 hours",
            "Aspirin 500mg - 1 tablet as needed"
          ],
          "Prescription": [
            "Sumatriptan (Imigran) 50mg - 1 tablet at onset, repeat after 2 hours if needed",
            "Propranolol 40mg - 1 tablet daily for prevention",
            "Topiramate (Topamax) 25mg - 1 tablet at night for chronic migraine"
          ]
        },
        "recommendations": [
          "Rest in quiet, dark room",
          "Avoid triggers (caffeine, stress, certain foods)",
          "Apply cold compress to head",
          "Stay hydrated",
          "Maintain regular sleep schedule"
        ],
        "when_to_see_doctor": "Neurology consultation for frequent migraines (>4/month)",
        "severity_level": "MODERATE"
      }
    ]
  }
}
```

**Key Points**:
- ✅ Migraine identified (75% confidence)
- ✅ 3 OTC options
- ✅ 3 Prescription options (Sumatriptan, Propranolol, Topiramate)
- ✅ Prevention recommendations included
- ✅ When to see neurologist

---

### **TEST 6: Diabetes** 🩺

**Input:**
```json
POST /api/diagnose
{
  "symptoms": "excessive thirst, frequent urination, fatigue, blurred vision",
  "severity": "moderate",
  "duration": "2 weeks"
}
```

**Expected Output:**
```json
{
  "success": true,
  "symptom_analysis": {
    "conditions": ["Diabetes Mellitus", "Thyroid Disorder"],
    "confidence": [0.80, 0.60],
    "detailed_recommendations": [
      {
        "description": "Elevated blood glucose levels",
        "symptoms": "Thirst, frequent urination, fatigue, blurred vision",
        "duration": "Chronic - lifelong management",
        "medications": {
          "OTC": [
            "Glucose monitoring test strips - use as recommended"
          ],
          "Prescription": [
            "Type 2 Oral: Metformin (Glucophage) 500mg - 1 tablet twice daily",
            "Sulfonylurea: Glipizide (Minidiab) 5mg - 1 tablet daily",
            "DPP-4 inhibitor: Sitagliptin (Januvia) 100mg - 1 tablet daily",
            "GLP-1 agonist: Dulaglutide (Trulicity) - 0.75mg-1.5mg injection weekly",
            "Insulin: Basal-bolus or long-acting insulin as required"
          ]
        },
        "recommendations": [
          "Follow diabetic diet plan",
          "Monitor blood glucose daily",
          "Exercise 30 minutes daily",
          "Maintain healthy weight",
          "Regular eye and foot exams",
          "Check HbA1c every 3 months"
        ],
        "when_to_see_doctor": "Monthly for Type 1; quarterly for Type 2. Blood glucose <70 or >300 → ER",
        "severity_level": "MODERATE (Chronic)"
      }
    ]
  }
}
```

**Key Points**:
- ✅ Diabetes identified with high confidence (80%)
- ✅ 5 Prescription medication options
- ✅ Chronic condition management guidance
- ✅ Monitoring requirements
- ✅ Emergency glucose levels specified

---

### **TEST 7: Skin Rash/Allergies** 🔴

**Input:**
```json
POST /api/diagnose
{
  "symptoms": "red itchy rash all over body, swelling",
  "severity": "moderate",
  "duration": "3 days"
}
```

**Expected Output:**
```json
{
  "success": true,
  "symptom_analysis": {
    "conditions": ["Skin Rash", "Allergic Rhinitis (Hay Fever)", "Eczema (Atopic Dermatitis)"],
    "confidence": [0.75, 0.65, 0.60],
    "detailed_recommendations": [
      {
        "description": "Non-infectious skin irritation or allergic reaction",
        "symptoms": "Itching, redness, swelling, skin texture change",
        "duration": "3-14 days depending on cause",
        "medications": {
          "OTC": [
            "Cetirizine (Alerid) 10mg - 1 tablet daily for itching",
            "Hydrocortisone cream 1% - apply 2-3 times daily",
            "Calamine lotion - apply as needed for relief",
            "Moisturizer (Cetaphil) - apply regularly"
          ],
          "Prescription": [
            "Betamethasone cream 0.05% - apply 2-3 times daily",
            "Mometasone (Momate) cream - 2-3 times daily",
            "Prednisone 10-20mg - if severe systemic allergic reaction"
          ]
        },
        "recommendations": [
          "Identify and avoid trigger",
          "Use mild soap and lukewarm water",
          "Apply moisturizer while skin damp",
          "Avoid scratching to prevent infection",
          "Keep area clean and dry"
        ],
        "when_to_see_doctor": "Rash spreads quickly, involves face/genitals, or with high fever",
        "severity_level": "MILD TO MODERATE"
      }
    ]
  }
}
```

**Key Points**:
- ✅ Rash identified (75% confidence)
- ✅ 4 OTC options with frequencies
- ✅ 3 Prescription alternatives
- ✅ Severity determination
- ✅ When to see doctor guidance

---

### **TEST 8: Asthma** 💨

**Input:**
```json
POST /api/diagnose
{
  "symptoms": "wheezing, shortness of breath, chest tightness, difficulty breathing",
  "severity": "moderate",
  "duration": "1 week"
}
```

**Expected Output:**
```json
{
  "success": true,
  "symptom_analysis": {
    "conditions": ["Asthma", "Bronchitis"],
    "confidence": [0.70, 0.65],
    "detailed_recommendations": [
      {
        "description": "Chronic airway inflammation causing breathing difficulty",
        "symptoms": "Wheezing, shortness of breath, chest tightness, cough",
        "duration": "Chronic condition",
        "medications": {
          "OTC": [
            "Salbutamol inhaler (Asthalin/Ventolin) - 2 puffs every 4-6 hours as needed"
          ],
          "Prescription": [
            "Fluticasone propionate inhaler (Flixonase) - 2 puffs twice daily",
            "Salmeterol xinafoate (Seretide) - 2 puffs twice daily",
            "Montelukast (Singulair) 10mg - 1 tablet daily at night",
            "Salbutamol inhaler - 2 puffs for acute attacks"
          ]
        },
        "recommendations": [
          "Avoid asthma triggers (allergens, pollution, cold air)",
          "Use peak flow meter daily",
          "Keep rescue inhaler always available",
          "Maintain medication routine",
          "Seek shelter from pollution and dust"
        ],
        "when_to_see_doctor": "Frequent attacks, inability to speak full sentences, or blue lips → ER",
        "severity_level": "MODERATE TO SEVERE"
      }
    ]
  }
}
```

**Key Points**:
- ✅ Asthma identified (70% confidence)
- ✅ OTC rescue inhaler
- ✅ 4 Prescription maintenance options
- ✅ Rescue vs maintenance distinction
- ✅ Emergency triggers specified

---

## 📊 TESTING SUMMARY TABLE

| Symptom Input | Disease Detected | Confidence | Top Medication |
|---------------|-----------------|-----------|-----------------|
| Cough, sore throat, runny nose | Common Cold | 80% | Paracetamol 500mg |
| Fever, body ache, cough, fatigue | Flu (Influenza) | 85% | Oseltamivir 75mg |
| Severe chest pain, breathing difficulty | EMERGENCY | 100% | Call 911 |
| Burning urination, frequency, pain | UTI | 82% | Ciprofloxacin 500mg |
| Severe headache, nausea, light sensitive | Migraine | 75% | Sumatriptan 50mg |
| Thirst, frequent urination, fatigue | Diabetes | 80% | Metformin 500mg |
| Red itchy rash, swelling | Skin Rash | 75% | Cetirizine 10mg |
| Wheezing, shortness of breath | Asthma | 70% | Salbutamol inhaler |

---

## 🔧 CURL COMMAND EXAMPLES

### Test 1: Cold
```bash
curl -X POST http://localhost:5000/api/diagnose \
  -F "symptoms=cough, sore throat, runny nose" \
  -F "severity=mild" \
  -F "duration=3 days"
```

### Test 2: Flu
```bash
curl -X POST http://localhost:5000/api/diagnose \
  -F "symptoms=fever, body ache, cough, and extreme fatigue" \
  -F "severity=moderate" \
  -F "duration=2 days"
```

### Test 3: Emergency
```bash
curl -X POST http://localhost:5000/api/diagnose \
  -F "symptoms=severe chest pain and difficulty breathing" \
  -F "severity=critical" \
  -F "duration=1 hour"
```

### Test 4: UTI
```bash
curl -X POST http://localhost:5000/api/diagnose \
  -F "symptoms=burning urination, frequent urges, lower abdominal pain" \
  -F "severity=moderate" \
  -F "duration=2 days"
```

---

## ✅ VERIFICATION CHECKLIST

After running each test, verify:

- ✅ Disease correctly identified
- ✅ Confidence score is reasonable (50-100%)
- ✅ OTC medications listed with dosages
- ✅ Prescription alternatives provided
- ✅ Medication brand names included
- ✅ Frequency specified (e.g., "every 6 hours")
- ✅ "When to see doctor" guidance present
- ✅ Recommendations provided
- ✅ Severity level indicated
- ✅ JSON response properly formatted

---

## 🎯 NEXT STEPS

1. **Test locally**: Run each test case above
2. **Verify responses**: Check all medication details
3. **Deploy to Kaggle**: Update notebook with new code
4. **Share results**: Show users comprehensive coverage

---

**System Ready for Testing**: ✅
**All 25+ Diseases Covered**: ✅
**50+ Medications Included**: ✅
**Emergency Detection**: ✅
**Production Ready**: ✅
