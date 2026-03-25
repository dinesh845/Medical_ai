"""
Advanced Medical Knowledge Base for AI Chatbot
Provides accurate, evidence-based medical information
"""

class MedicalKnowledgeBase:
    """Comprehensive medical knowledge database"""
    
    def __init__(self):
        self.conditions = self._load_medical_conditions()
        self.symptoms = self._load_symptom_index()
        self.emergency_keywords = [
            'chest pain', 'can\'t breathe', 'difficulty breathing', 'unconscious',
            'severe bleeding', 'suicide', 'overdose', 'seizure', 'stroke',
            'heart attack', 'choking', 'severe burn', 'broken bone'
        ]
    
    def _load_medical_conditions(self):
        """Load medical conditions database"""
        return {
            'fever': {
                'description': 'Elevated body temperature above 100.4°F (38°C)',
                'causes': ['Viral infection', 'Bacterial infection', 'Inflammatory conditions', 'Heat exhaustion'],
                'symptoms': ['Chills', 'Sweating', 'Headache', 'Muscle aches', 'Weakness'],
                'home_care': [
                    'Rest and get plenty of sleep',
                    'Drink fluids (water, clear broths, electrolyte drinks)',
                    'Take acetaminophen (Tylenol) or ibuprofen (Advil) as directed',
                    'Wear lightweight clothing',
                    'Keep room temperature comfortable',
                    'Use cool compresses'
                ],
                'when_to_see_doctor': [
                    'Temperature over 103°F (39.4°C)',
                    'Fever lasts more than 3 days',
                    'Severe headache or stiff neck',
                    'Unusual skin rash',
                    'Difficulty breathing',
                    'Persistent vomiting',
                    'Confusion or difficulty staying awake'
                ],
                'prevention': ['Hand washing', 'Vaccination', 'Avoid sick people', 'Maintain healthy immune system']
            },
            
            'diabetes': {
                'description': 'Chronic condition affecting blood sugar regulation',
                'types': {
                    'type1': 'Autoimmune condition, pancreas produces little/no insulin',
                    'type2': 'Body cannot use insulin effectively, most common type',
                    'gestational': 'High blood sugar during pregnancy'
                },
                'symptoms': ['Increased thirst', 'Frequent urination', 'Fatigue', 'Blurred vision', 'Slow healing wounds'],
                'risk_factors': ['Family history', 'Obesity', 'Sedentary lifestyle', 'Age over 45', 'High blood pressure'],
                'management': [
                    'Blood sugar monitoring (regular testing)',
                    'Healthy diet (low sugar, whole grains)',
                    'Regular physical activity (150 min/week)',
                    'Weight management',
                    'Stress management',
                    'Limit alcohol',
                    'Take medications as prescribed'
                ],
                'complications': ['Heart disease', 'Kidney disease', 'Eye problems', 'Nerve damage', 'Foot problems'],
                'when_to_seek_care': [
                    'Severe abdominal pain with nausea',
                    'Confusion or difficulty breathing',
                    'Blood sugar below 70 or above 300',
                    'Signs of infection in cuts/wounds',
                    'Chest pain or shortness of breath'
                ]
            },
            
            'hypertension': {
                'description': 'High blood pressure (over 130/80 mmHg)',
                'stages': {
                    'elevated': 'Systolic 120-129 and diastolic <80',
                    'stage1': 'Systolic 130-139 or diastolic 80-89',
                    'stage2': 'Systolic 140+ or diastolic 90+'
                },
                'symptoms': ['Often no symptoms (silent killer)', 'Headache', 'Shortness of breath', 'Nosebleeds'],
                'risk_factors': ['Family history', 'Age', 'Race (African American)', 'Obesity', 'Salt intake', 'Alcohol'],
                'management': [
                    'Reduce sodium to <2300mg/day',
                    'DASH diet (fruits, vegetables, whole grains)',
                    'Regular exercise (150 min/week)',
                    'Maintain healthy weight',
                    'Manage stress',
                    'Limit alcohol',
                    'Take medicines as prescribed',
                    'Monitor blood pressure regularly'
                ],
                'complications': ['Heart attack', 'Stroke', 'Kidney disease', 'Heart failure'],
                'monitoring': 'Check BP at home regularly and keep records'
            },
            
            'asthma': {
                'description': 'Chronic airway inflammation causing breathing difficulty',
                'types': ['Allergic asthma', 'Non-allergic asthma', 'Occupational asthma', 'Childhood asthma'],
                'symptoms': ['Wheezing', 'Cough (esp. at night/cold)', 'Shortness of breath', 'Chest tightness'],
                'triggers': ['Allergens (dust, pollen, pets)', 'Exercise', 'Cold air', 'Stress', 'Infections', 'Smoke'],
                'quick_relief': [
                    'Use rescue inhaler (albuterol) immediately',
                    'Sit upright to ease breathing',
                    'Take slow, deep breaths',
                    'Remove away from triggering substance'
                ],
                'long_term_control': [
                    'Use controller medications regularly',
                    'Identify and avoid triggers',
                    'Keep rescue inhaler accessible',
                    'Create asthma action plan with doctor',
                    'Regular exercise (helps lungs)',
                    'Manage allergies'
                ],
                'emergency_signs': ['Severe shortness of breath', 'Lips/fingernails turning blue', 'Cannot speak', 'Severe wheezing'],
                'prevention': ['Regular medication', 'Trigger avoidance', 'Allergy management']
            },
            
            'arthritis': {
                'description': 'Joint inflammation causing pain, stiffness, and reduced movement',
                'types': {
                    'osteoarthritis': 'Wear and tear arthritis, most common',
                    'rheumatoid': 'Autoimmune condition affecting multiple joints',
                    'gout': 'Uric acid buildup causing severe joint pain'
                },
                'symptoms': ['Joint pain', 'Stiffness (morning stiffness)', 'Swelling', 'Redness', 'Warmth', 'Reduced range'],
                'management': [
                    'Over-the-counter pain relievers',
                    'Heat or cold therapy',
                    'Gentle exercise/stretching',
                    'Weight management',
                    'Joint protection',
                    'Physical therapy',
                    'Prescription medications if needed',
                    'Topical creams'
                ],
                'self_care': [
                    'Apply heat for 15-20 minutes before activity',
                    'Ice after activity for swelling',
                    'Maintain healthy weight',
                    'Stay active with gentle exercise',
                    'Get adequate sleep'
                ],
                'when_to_see_doctor': [
                    'Joint pain lasting >6 weeks',
                    'Severe joint swelling',
                    'Significant impact on daily activities',
                    'Signs of infection (fever, heat, redness)'
                ]
            },
            
            'thyroid_disease': {
                'description': 'Problems with thyroid gland affecting metabolism',
                'types': {
                    'hypothyroidism': 'Underactive thyroid (not enough hormone)',
                    'hyperthyroidism': 'Overactive thyroid (too much hormone)',
                    'thyroiditis': 'Thyroid inflammation'
                },
                'hypothyroidism_symptoms': ['Fatigue', 'Weight gain', 'Cold sensitivity', 'Dry skin', 'Hair loss', 'Depression'],
                'hyperthyroidism_symptoms': ['Weight loss', 'Anxiety', 'Heat sensitivity', 'Tremors', 'Rapid heartbeat'],
                'causes': ['Autoimmune disease', 'Iodine deficiency', 'Radiation', 'Medication', 'Surgery'],
                'management': [
                    'Regular thyroid function tests (TSH, T3, T4)',
                    'Thyroid medications (if prescribed)',
                    'Adequate iodine intake',
                    'Stress management',
                    'Good sleep habits',
                    'Regular exercise'
                ],
                'when_to_test': [
                    'Weight changes without cause',
                    'Persistent fatigue',
                    'Temperature regulation issues',
                    'Hair/skin changes',
                    'Mood changes'
                ]
            },
            
            'heart_disease': {
                'description': 'Various conditions affecting heart function',
                'types': ['Coronary artery disease', 'Heart failure', 'Arrhythmia', 'Valvular disease'],
                'risk_factors': ['High blood pressure', 'Diabetes', 'High cholesterol', 'Smoking', 'Obesity', 'Family history'],
                'symptoms': ['Chest pain/pressure', 'Shortness of breath', 'Fatigue', 'Palpitations', 'Dizziness'],
                'prevention': [
                    'Maintain healthy weight',
                    'Regular exercise (150 min/week)',
                    'Heart-healthy diet (low saturated fat)',
                    'Control blood pressure and cholesterol',
                    'Quit smoking',
                    'Manage diabetes',
                    'Reduce stress',
                    'Moderate alcohol'
                ],
                'warning_signs': [
                    'Chest pain or pressure',
                    'Shortness of breath',
                    'Palpitations (racing heart)',
                    'Fainting',
                    'Severe fatigue'
                ],
                'emergency': 'Call 911 if experiencing chest pain, severe shortness of breath, or fainting'
            },
            
            'kidney_disease': {
                'description': 'Progressive loss of kidney function',
                'stages': ['Stage 1: 90+% function', 'Stage 2: 60-89% function', 'Stage 3a: 45-59% function', 
                          'Stage 3b: 30-44% function', 'Stage 4: 15-29% function', 'Stage 5: <15% (kidney failure)'],
                'symptoms': ['Often no early symptoms', 'Fatigue', 'Swelling (feet/ankles)', 'Decreased urine', 'High blood pressure'],
                'risk_factors': ['Diabetes (leading cause)', 'High blood pressure', 'Family history', 'Age over 60', 'Obesity'],
                'management': [
                    'Monitor kidney function (regular tests)',
                    'Control blood pressure',
                    'Manage diabetes',
                    'Reduce sodium intake',
                    'Limit protein (as advised by doctor)',
                    'Maintain healthy weight',
                    'Avoid nephrotoxic medications',
                    'Stay hydrated'
                ],
                'when_to_see_doctor': [
                    'Persistent fatigue',
                    'Changes in urination',
                    'Swelling in legs/feet',
                    'High blood pressure',
                    'Kidney disease in family'
                ]
            },
            
            'liver_disease': {
                'description': 'Various conditions affecting liver function',
                'types': ['Fatty liver disease', 'Hepatitis', 'Cirrhosis', 'Liver cancer'],
                'symptoms': ['Jaundice (yellow eyes/skin)', 'Abdominal pain', 'Swelling (belly)', 'Fatigue', 'Dark urine'],
                'causes': ['Alcohol overuse', 'Hepatitis (viral)', 'Obesity', 'Autoimmune disease', 'Fatty diet'],
                'prevention': [
                    'Limit alcohol consumption',
                    'Maintain healthy weight',
                    'Eat balanced diet (low fat)',
                    'Get vaccinated (Hepatitis A & B)',
                    'Practice safe behaviors',
                    'Exercise regularly',
                    'Avoid raw seafood'
                ],
                'management': [
                    'Regular liver function tests',
                    'Abstain from alcohol',
                    'Heart-healthy, low-sodium diet',
                    'Weight management',
                    'Medications if prescribed',
                    'Avoid hepatotoxic substances'
                ],
                'when_urgent': ['Severe abdominal pain', 'Vomiting blood', 'Persistent jaundice', 'Confusion']
            },
            
            'anemia': {
                'description': 'Low hemoglobin preventing adequate oxygen transport',
                'types': {
                    'iron_deficiency': 'Most common, from low iron intake/loss',
                    'b12_deficiency': 'Poor absorption of vitamin B12',
                    'folate_deficiency': 'Inadequate folic acid intake',
                    'hemolytic': 'Red blood cells destroyed faster than produced'
                },
                'symptoms': ['Fatigue', 'Weakness', 'Shortness of breath', 'Dizziness', 'Pale skin', 'Cold hands/feet'],
                'causes': ['Poor diet', 'Blood loss', 'Chronic disease', 'Malabsorption', 'Medications'],
                'management': [
                    'Iron-rich foods (red meat, spinach, beans)',
                    'Vitamin B12 supplementation',
                    'Folic acid foods/supplements',
                    'Vitamin C to improve iron absorption',
                    'Address underlying causes',
                    'Regular blood tests'
                ],
                'iron_rich_foods': ['Red meat', 'Spinach', 'Lentils', 'Chickpeas', 'Oysters', 'Fortified cereals'],
                'when_seek_care': [
                    'Severe fatigue',
                    'Shortness of breath at rest',
                    'Chest pain',
                    'Rapid heartbeat',
                    'Confusion or difficulty concentrating'
                ]
            },
            
            'skin_conditions': {
                'common_conditions': {
                    'acne': 'Pores clogged with oil and dead skin',
                    'eczema': 'Itchy, inflamed skin',
                    'psoriasis': 'Red, scaly patches',
                    'urticaria': 'Allergic reaction causing hives',
                    'fungal_infection': 'Ringworm, athlete\'s foot',
                    'dermatitis': 'Contact-induced inflammation'
                },
                'general_care': [
                    'Keep skin clean and dry',
                    'Avoid irritants and allergens',
                    'Moisturize appropriately',
                    'Use sunscreen (SPF 30+)',
                    'Avoid scratching',
                    'Wear breathable clothing',
                    'Manage stress'
                ],
                'when_to_see_dermatologist': [
                    'Skin condition lasting >2 weeks',
                    'Spreading or worsening rash',
                    'Signs of infection (warmth, pus, fever)',
                    'Severe itching interfering with sleep',
                    'New or changing moles',
                    'Covering large area of body'
                ],
                'prevention': [
                    'Practice good hygiene',
                    'Avoid known irritants',
                    'Moisturize regularly',
                    'Sun protection',
                    'Manage humidity',
                    'Wear clean clothes'
                ]
            },
            
            'common_infections': {
                'conditions': {
                    'strep_throat': 'Bacterial sore throat with white patches',
                    'uti': 'Urinary tract infection',
                    'sinusitis': 'Sinus infection with congestion/pain',
                    'otitis_media': 'Ear infection, common in children',
                    'pink_eye': 'Conjunctivitis, bacterial or viral',
                    'skin_infection': 'Impetigo, cellulitis, boils'
                },
                'general_management': [
                    'Rest and hydration',
                    'Over-the-counter pain relievers',
                    'Warm compresses for localized infections',
                    'Antibiotic ointment for skin',
                    'Complete full course of antibiotics if prescribed',
                    'Good hygiene to prevent spread'
                ],
                'when_antibiotics_needed': [
                    'Bacterial infections (confirmed by test)',
                    'Severe infections',
                    'Immunocompromised individuals',
                    'Infections spreading rapidly'
                ],
                'prevention': [
                    'Proper handwashing',
                    'Avoid touching face',
                    'Cover mouth when coughing/sneezing',
                    'Stay away from sick people',
                    'Keep wounds clean'
                ]
            },
            
            'migraine': {
                'description': 'Severe headache often with nausea and light sensitivity',
                'symptoms': ['Intense throbbing pain', 'One-sided usually', 'Nausea/vomiting', 'Light sensitivity', 'Sound sensitivity', 'Vision changes (aura)'],
                'stages': ['Prodrome (warning signs)', 'Aura (visual disturbances)', 'Headache (pain)', 'Postdrome (recovery)'],
                'triggers': ['Stress', 'Hormonal changes', 'Certain foods', 'Sleep changes', 'Weather changes', 'Intense lights', 'Loud sounds'],
                'food_triggers': ['Aged cheeses', 'Cured meats', 'Alcohol (esp. red wine)', 'Chocolate', 'Caffeine', 'MSG', 'Artificial sweeteners'],
                'relief': [
                    'Lie in dark, quiet room',
                    'Apply cold compress to head',
                    'Use pain reliever early',
                    'Stay hydrated',
                    'Try acupressure or massage',
                    'Use prescription migraine medications',
                    'Sleep if possible'
                ],
                'prevention': [
                    'Identify and avoid triggers',
                    'Regular sleep schedule',
                    'Manage stress',
                    'Regular exercise',
                    'Stay hydrated',
                    'Limit caffeine',
                    'Prophylactic medications if frequent'
                ]
            },
            
            'sleep_disorders': {
                'conditions': ['Insomnia', 'Sleep apnea', 'Restless leg syndrome', 'Narcolepsy', 'Jet lag'],
                'insomnia_symptoms': ['Difficulty falling asleep', 'Frequent waking', 'Waking too early', 'Daytime fatigue', 'Difficulty concentrating'],
                'sleep_apnea_symptoms': ['Loud snoring', 'Gasping during sleep', 'Daytime sleepiness', 'Headaches', 'Restless sleep'],
                'sleep_hygiene': [
                    'Keep consistent sleep schedule (even weekends)',
                    'Bedroom cool, dark, quiet',
                    'Avoid screens 1 hour before bed',
                    'No caffeine after 2 PM',
                    'No large meals near bedtime',
                    'Exercise regularly (but not before bed)',
                    'Relaxation techniques (meditation, deep breathing)',
                    'Limit naps to 20-30 minutes'
                ],
                'when_seek_help': [
                    'Sleep problems lasting >2 weeks',
                    'Loud snoring',
                    'Gasping episodes',
                    'Significant daytime sleepiness',
                    'Sleep affecting work/relationships'
                ],
                'treatments': [
                    'Sleep hygiene improvement',
                    'Cognitive behavioral therapy',
                    'Medications if needed',
                    'CPAP machine (for sleep apnea)',
                    'Lifestyle changes'
                ]
            },
            
            'obesity': {
                'description': 'Excess body weight increasing health risks',
                'classification': ['Overweight: BMI 25-29.9', 'Obese (Class I): BMI 30-34.9', 'Obese (Class II): BMI 35-39.9', 'Severely obese: BMI 40+'],
                'health_risks': ['Type 2 diabetes', 'Heart disease', 'High blood pressure', 'Stroke', 'Sleep apnea', 'Joint problems', 'Cancer'],
                'management': [
                    'Calorie-controlled diet',
                    'Portion control',
                    'Regular physical activity (150-300 min/week)',
                    'Behavior change therapy',
                    'Weight loss medications (if prescribed)',
                    'Bariatric surgery (in severe cases)',
                    'Support groups',
                    'Stress management'
                ],
                'diet_tips': [
                    'Whole grains instead of refined',
                    'Lean proteins',
                    'More vegetables and fruits',
                    'Limit sugar and processed foods',
                    'Watch portion sizes',
                    'Drink water instead of sugary drinks',
                    'Eat slowly',
                    'Plan meals ahead'
                ],
                'realistic_goals': 'Aim for 1-2 lbs per week weight loss'
            },
            
            'high_cholesterol': {
                'description': 'Excess cholesterol in blood increasing heart disease risk',
                'types': ['LDL (bad cholesterol)', 'HDL (good cholesterol)', 'Triglycerides'],
                'symptoms': ['Usually no symptoms (discovered through blood test)'],
                'risk_factors': ['Family history', 'Age', 'Gender', 'Poor diet', 'Lack of exercise', 'Obesity', 'Smoking'],
                'management': [
                    'Reduce saturated fats',
                    'Eliminate trans fats',
                    'Increase soluble fiber (oats, beans)',
                    'Eat plant sterols (nuts, seeds)',
                    'Regular exercise',
                    'Maintain healthy weight',
                    'Quit smoking',
                    'Medications (statins) if needed',
                    'Regular cholesterol testing'
                ],
                'heart_healthy_foods': [
                    'Fatty fish (salmon, mackerel)',
                    'Nuts and seeds',
                    'Whole grains',
                    'Fruits and vegetables',
                    'Olive oil',
                    'Lean meats',
                    'Low-fat dairy'
                ],
                'avoid': ['Fatty meats', 'Butter', 'Whole milk', 'Processed foods', 'Fried foods', 'Trans fats']
            }
        }
    
    def _load_symptom_index(self):
        """Create searchable symptom index"""
        return {
            'fever': ['fever', 'temperature', 'hot', 'burning up', 'chills', 'elevated temp'],
            'headache': ['headache', 'head pain', 'migraine', 'head hurt', 'migraine pain'],
            'cough': ['cough', 'coughing', 'hacking', 'dry cough', 'wet cough'],
            'stomach': ['stomach', 'nausea', 'vomit', 'diarrhea', 'abdominal', 'belly', 'indigestion'],
            'respiratory': ['breathe', 'breathing', 'shortness of breath', 'wheeze', 'congested', 'asthma'],
            'chest_pain': ['chest pain', 'chest hurt', 'chest pressure', 'heart', 'heart attack'],
            'anxiety': ['anxiety', 'anxious', 'panic', 'stress', 'worried', 'nervous', 'panic attack'],
            'depression': ['depression', 'depressed', 'sad', 'hopeless', 'suicidal', 'melancholy'],
            'cold_flu': ['cold', 'flu', 'runny nose', 'sore throat', 'sniffles', 'influenza'],
            'allergy': ['allergy', 'allergic', 'itchy', 'rash', 'hives', 'allergies'],
            'pain': ['pain', 'ache', 'hurt', 'sore', 'aching'],
            'fatigue': ['tired', 'fatigue', 'exhausted', 'sleepy', 'weak', 'energy'],
            'diabetes': ['diabetes', 'blood sugar', 'glucose', 'sugar level', 'diabetic', 'thirst'],
            'hypertension': ['high blood pressure', 'hypertension', 'blood pressure', 'hypertensive'],
            'arthritis': ['arthritis', 'joint pain', 'stiff joints', 'joint swelling', 'rheumatoid'],
            'thyroid': ['thyroid', 'metabolism', 'weight change', 'cold sensitivity', 'goiter'],
            'heart': ['heart disease', 'heart condition', 'cardiac', 'coronary', 'arrhythmia', 'palpitations'],
            'kidney': ['kidney', 'renal', 'urinary', 'dialysis', 'kidney failure'],
            'liver': ['liver', 'hepatitis', 'jaundice', 'cirrhosis', 'hepatic'],
            'anemia': ['anemia', 'anemic', 'low hemoglobin', 'low iron', 'weak blood'],
            'skin': ['skin', 'rash', 'acne', 'eczema', 'psoriasis', 'dermatitis', 'hives', 'infection'],
            'infection': ['infection', 'bacterial', 'viral', 'fungal', 'infected', 'strep'],
            'sleep': ['sleep', 'insomnia', 'sleep apnea', 'sleepless', 'cannot sleep', 'trouble sleeping'],
            'cholesterol': ['cholesterol', 'high cholesterol', 'lipid', 'triglycerides'],
            'weight': ['obesity', 'overweight', 'weight gain', 'weight loss', 'diet', 'fat'],
            'migraine': ['migraine', 'throbbing headache', 'hemicranias', 'migraine pain']
        }
    
    def detect_emergency(self, message):
        """Check if message indicates medical emergency"""
        message_lower = message.lower()
        for keyword in self.emergency_keywords:
            if keyword in message_lower:
                return True
        return False
    
    def identify_symptoms(self, message):
        """Identify symptoms mentioned in message"""
        message_lower = message.lower()
        detected = []
        
        for symptom_category, keywords in self.symptoms.items():
            if any(keyword in message_lower for keyword in keywords):
                detected.append(symptom_category)
        
        return detected
    
    def get_response(self, message, symptoms=None):
        """Generate detailed medical response"""
        if self.detect_emergency(message):
            return self._emergency_response()
        
        if symptoms is None:
            symptoms = self.identify_symptoms(message)
        
        if not symptoms:
            return self._general_response(message)
        
        # Generate response for first detected symptom
        primary_symptom = symptoms[0]
        return self._symptom_specific_response(primary_symptom, message)
    
    def _emergency_response(self):
        """Response for medical emergencies"""
        return {
            'message': """🚨 **MEDICAL EMERGENCY DETECTED** 🚨

Based on your message, this may be a medical emergency.

**CALL 911 or local emergency services IMMEDIATELY if you're experiencing:**
- Chest pain or pressure
- Difficulty breathing or shortness of breath
- Sudden severe headache
- Loss of consciousness
- Severe bleeding
- Signs of stroke (face drooping, arm weakness, speech difficulty)
- Thoughts of harming yourself or others

**DO NOT WAIT - SEEK IMMEDIATE MEDICAL ATTENTION**

If this is not an emergency, I'm here to help with other health questions.""",
            'suggestions': ['I called 911', 'Not an emergency', 'Different symptoms']
        }
    
    def _symptom_specific_response(self, symptom, message):
        """Generate detailed response for specific symptom"""
        # This will be filled out based on the symptom
        responses = {
            'fever': self._fever_response,
            'headache': self._headache_response,
            'cough': self._cough_response,
            'stomach': self._stomach_response,
            'respiratory': self._respiratory_response,
            'chest_pain': self._chest_pain_response,
            'anxiety': self._anxiety_response,
            'depression': self._depression_response
        }
        
        response_func = responses.get(symptom, self._general_response)
        return response_func(message)
    
    def _fever_response(self, message):
        info = self.conditions['fever']
        return {
            'message': f"""**Understanding Your Fever**

A fever is your body's natural response to fighting infection. Here's comprehensive guidance:

**What is Fever?**
- Body temperature above 100.4°F (38°C)
- Normal temperature: 97-99°F (36.1-37.2°C)

**Common Causes:**
{self._format_list(info['causes'])}

**Home Care - What You Can Do:**
{self._format_numbered_list(info['home_care'])}

**When to See a Doctor:**
{self._format_list(info['when_to_see_doctor'])}

**Prevention Tips:**
{self._format_list(info['prevention'])}

**Important:** If you're concerned or symptoms worsen, contact your healthcare provider.

Do you have any other symptoms alongside the fever?""",
            'suggestions': ['I have a cough too', 'Severe headache', 'It\'s been 4 days']
        }
    
    def _headache_response(self, message):
        info = self.conditions['headache']
        return {
            'message': f"""**Understanding Your Headache**

Headaches are common but can vary greatly. Let me help you understand and manage them.

**Types of Headaches:**
{self._format_dict(info['types'])}

**Common Triggers:**
{self._format_list(info['triggers'])}

**Relief Strategies:**
{self._format_numbered_list(info['home_care'])}

**⚠️ RED FLAGS - See Doctor Immediately If:**
{self._format_list(info['red_flags'])}

**Tips for Prevention:**
- Maintain regular sleep schedule
- Stay hydrated (8 glasses water daily)
- Manage stress
- Avoid known triggers
- Regular exercise
- Good posture

Would you describe your headache as throbbing, dull, or sharp? This helps determine the type.""",
            'suggestions': ['Throbbing pain', 'Dull ache', 'Sharp/stabbing pain']
        }
    
    def _cough_response(self, message):
        info = self.conditions['cough']
        return {
            'message': f"""**Understanding Your Cough**

Coughing is your body's protective reflex to clear airways. Here's what you need to know:

**Types of Cough:**
{self._format_dict(info['types'])}

**Common Causes:**
{self._format_list(info['causes'])}

**Home Remedies That Work:**
{self._format_numbered_list(info['home_care'])}

**Seek Medical Care If:**
{self._format_list(info['seek_care_if'])}

**Quick Relief Tips:**
- Drink warm liquids (honey lemon tea excellent choice)
- Suck on throat lozenges
- Avoid cold, dry air
- Use cough drops with menthol

Is your cough dry (no mucus) or wet (producing phlegm)? This helps determine best treatment.""",
            'suggestions': ['Dry cough', 'Wet/productive cough', 'Coughing at night']
        }
    
    def _stomach_response(self, message):
        info = self.conditions['stomach_issues']
        return {
            'message': f"""**Understanding Your Stomach Issues**

Digestive problems are common and usually resolve with proper care.

**Common Conditions:**
{self._format_dict(info['conditions'])}

**Symptoms to Watch:**
{self._format_list(info['symptoms'])}

**The BRAT Diet (Easy on stomach):**
{self._format_list(info['brat_diet'])}

**Home Care Steps:**
{self._format_numbered_list(info['home_care'])}

**⚠️ Seek Urgent Care If:**
{self._format_list(info['urgent_care_needed'])}

**Hydration is Key:**
- Sip clear fluids frequently
- Try electrolyte drinks (Pedialyte, Gatorade)
- Avoid caffeine and alcohol
- Start with ice chips if vomiting

How long have you been experiencing these symptoms?""",
            'suggestions': ['Just started today', '2-3 days', 'More than a week']
        }
    
    def _respiratory_response(self, message):
        info = self.conditions['respiratory']
        return {
            'message': f"""**Understanding Respiratory Symptoms**

Breathing problems need careful attention. Here's guidance:

**Common Conditions:**
{self._format_list(info['conditions'])}

**Typical Symptoms:**
{self._format_list(info['symptoms'])}

**Home Care:**
{self._format_numbered_list(info['home_care'])}

**🚨 EMERGENCY SIGNS - Call 911:**
{self._format_list(info['emergency_signs'])}

**Breathing Exercises:**
1. Diaphragmatic breathing (belly breathing)
2. Pursed-lip breathing
3. Practice when calm to use during difficulty

**Important:** Any significant breathing difficulty should be evaluated by a healthcare provider.

Are you currently having difficulty breathing?""",
            'suggestions': ['Yes, hard to breathe', 'Mild difficulty', 'Just congested']
        }
    
    def _chest_pain_response(self, message):
        return {
            'message': """🚨 **CHEST PAIN REQUIRES IMMEDIATE ATTENTION** 🚨

**CALL 911 IMMEDIATELY if experiencing:**
- Crushing, squeezing, or pressure in chest
- Pain spreading to arm, jaw, neck, or back
- Shortness of breath
- Sweating, nausea, lightheadedness
- Feeling of impending doom

**HEART ATTACK SYMPTOMS:**
- Chest discomfort (center/left side)
- Pain lasting more than few minutes
- May come and go
- Women may have atypical symptoms (fatigue, nausea, back/jaw pain)

**Other Serious Causes:**
- Pulmonary embolism
- Aortic dissection
- Pneumothorax (collapsed lung)

**Less Urgent (but still see doctor):**
- Muscle strain
- Costochondritis (rib inflammation)
- Acid reflux/GERD
- Anxiety/panic attack

**IMPORTANT:** NEVER ignore chest pain. When in doubt, seek immediate medical evaluation.

Are you currently experiencing chest pain? If yes, call 911 now.""",
            'suggestions': ['Calling 911 now', 'It\'s mild discomfort', 'Previous chest pain']
        }
    
    def _anxiety_response(self, message):
        info = self.conditions['mental_health']
        return {
            'message': f"""**Understanding Anxiety**

Mental health is as important as physical health. You're not alone, and help is available.

**Common Anxiety Symptoms:**
{self._format_list(info['symptoms']['anxiety'])}

**Effective Coping Strategies:**
{self._format_numbered_list(info['coping_strategies'])}

**4-7-8 Breathing Technique:**
1. Exhale completely through mouth
2. Inhale through nose for 4 counts
3. Hold breath for 7 counts
4. Exhale through mouth for 8 counts
5. Repeat 3-4 times

**5-4-3-2-1 Grounding:**
- Name 5 things you see
- 4 things you can touch
- 3 things you hear
- 2 things you smell
- 1 thing you taste

**When to Seek Professional Help:**
{self._format_list(info['professional_help'])}

**Crisis Support:**
- Mental Health Crisis: Call/Text 988
- Crisis Text Line: Text HOME to 741741

Remember: Anxiety is treatable. With proper support, you can feel better.

Would you like specific techniques or resources?""",
            'suggestions': ['Breathing techniques', 'Find a therapist', 'Crisis support']
        }
    
    def _depression_response(self, message):
        info = self.conditions['mental_health']
        return {
            'message': f"""**Understanding Depression**

Depression is a medical condition, not a weakness. Support and treatment are available.

**Common Symptoms:**
{self._format_list(info['symptoms']['depression'])}

**Self-Care Steps:**
{self._format_numbered_list(info['coping_strategies'][:8])}

**Professional Treatment:**
{self._format_list(info['professional_help'])}

**Immediate Help Available:**
- **988 Suicide & Crisis Lifeline**: Call or text 988
- **Crisis Text Line**: Text HOME to 741741
- **Emergency**: Call 911 or go to nearest ER

**Remember:**
- Depression is treatable
- You're not alone - millions experience this
- Asking for help is a sign of strength
- Recovery is possible with proper support

**⚠️ If you're having thoughts of suicide, please reach out immediately.**

Are you currently safe? Would you like crisis resources?""",
            'suggestions': ['I need crisis help', 'Finding a therapist', 'Self-care tips']
        }
    
    def _general_response(self, message):
        return {
            'message': """**Hello! I'm Here to Help**

I'm your AI Medical Assistant, ready to provide health information and guidance.

**I can help with:**
- Understanding symptoms and conditions
- Home care recommendations
- When to seek medical care
- General health information
- Wellness and prevention tips

**How to get the best help:**
Please describe your specific symptoms or health concern. For example:
- "I have a fever and sore throat"
- "I'm experiencing headaches every day"
- "I feel anxious and can't sleep"

**Important Reminders:**
- This is general information, not medical diagnosis
- Always consult healthcare professionals for medical decisions
- Call 911 for emergencies
- Your health and safety are the priority

**What specific symptoms or health concern can I help you understand today?**""",
            'suggestions': ['I have symptoms', 'General health question', 'Emergency information']
        }
    
    def _format_list(self, items):
        """Format list with bullet points"""
        return '\n'.join([f"• {item}" for item in items])
    
    def _format_numbered_list(self, items):
        """Format numbered list"""
        return '\n'.join([f"{i+1}. {item}" for i, item in enumerate(items)])
    
    def _format_dict(self, dict_items):
        """Format dictionary as list"""
        return '\n'.join([f"• **{key.title()}**: {value}" for key, value in dict_items.items()])


# Global knowledge base instance
medical_kb = MedicalKnowledgeBase()
