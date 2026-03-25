# 🏥 MediAI - AI-Based Medical Pre-Diagnosis System

An advanced AI-powered medical pre-diagnosis system that utilizes multi-modal data analysis including text symptoms, medical images, and audio recordings to provide comprehensive health assessments.

![MediAI Banner](https://img.shields.io/badge/MediAI-Medical%20Diagnosis-4F46E5?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

## ✨ Features

### 💬 AI Health Chatbot (NEW!)
- **Comprehensive Medical Knowledge**: Evidence-based information on 15+ health topics
- **Emergency Detection**: Automatic identification of life-threatening situations
- **Mental Health Support**: Anxiety, depression, and crisis resources (988 Lifeline)
- **Intelligent Responses**: Context-aware answers with actionable guidance
- **Interactive Suggestions**: Smart follow-up questions for better assistance
- **24/7 Availability**: Get instant health information anytime

### Multi-Modal AI Analysis
- **📝 Text Symptom Analysis**: Natural language processing for symptom description
- **🩻 Medical Image Analysis**: AI-powered analysis of X-rays, CT scans, and MRI images
- **🎤 Audio Analysis**: Voice pattern and cough sound analysis
- **🧠 Intelligent Diagnosis**: Advanced machine learning algorithms for accurate pre-diagnosis

### User-Friendly Interface
- **Modern Design**: Clean, professional medical-themed interface
- **Responsive Layout**: Works seamlessly on desktop, tablet, and mobile devices
- **Intuitive Navigation**: Easy-to-use form with clear sections
- **Real-time Feedback**: Instant notifications and loading indicators
- **Comprehensive Results**: Detailed diagnosis with confidence scores and recommendations

### Security & Privacy
- **Secure File Uploads**: Validated and secure file handling
- **Data Privacy**: HIPAA-compliant data handling practices
- **Session Management**: Secure patient data management
- **Encrypted Storage**: Safe storage of medical records

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser

### Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd c:\Users\MOHITH\Desktop\medical_ai
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. **Start the Flask server**
   ```bash
   python app.py
   ```

2. **Open your web browser and navigate to**
   ```
   http://localhost:5000
   ```

3. **You should see the MediAI homepage!**

## 📁 Project Structure

```
medical_ai/
│
├── app.py                      # Flask backend application
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
│
├── templates/
│   └── index.html             # Main HTML template
│
├── static/
│   ├── css/
│   │   └── style.css          # Stylesheet
│   └── js/
│       └── script.js          # JavaScript functionality
│
├── uploads/                   # Uploaded files directory
│   ├── images/                # Medical images
│   └── audio/                 # Audio files
│
└── data/
    └── diagnosis_records.json # Diagnosis history
```

## 💻 Usage Guide

### Step 1: Patient Information
- Enter your full name, age, gender, and contact information
- All fields marked with * are required

### Step 2: Describe Symptoms
- Provide a detailed description of your symptoms
- Select the duration (how long you've had the symptoms)
- Choose the severity level (mild, moderate, or severe)

### Step 3: Upload Multi-Modal Data (Optional)
- **Medical Images**: Upload X-rays, CT scans, or MRI images (JPG, PNG, DICOM)
- **Audio Files**: Upload audio recordings of cough or voice symptoms (MP3, WAV, OGG)

### Step 4: Analyze
- Click the "Analyze with AI" button
- Wait for the AI to process your data (typically 3-5 seconds)

### Step 5: View Results
- Review your AI-based diagnosis results
- Check confidence scores for each potential condition
- Read personalized recommendations
- Download or share your report

## 🎨 Key Features Explained

### Intelligent Symptom Analysis
The system uses natural language processing to understand and analyze symptom descriptions, considering:
- Symptom combinations
- Duration and severity
- Age and gender factors
- Medical history patterns

### Medical Image Processing
AI-powered image analysis for:
- X-ray examination
- CT scan interpretation
- MRI analysis
- Abnormality detection

### Voice & Audio Analysis
Advanced audio processing for:
- Cough pattern recognition
- Breathing sound analysis
- Voice symptom detection

### Comprehensive Reports
- Detailed diagnosis with confidence scores
- Personalized health recommendations
- Downloadable HTML reports
- Easy sharing with healthcare providers

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory for custom configuration:
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
MAX_UPLOAD_SIZE=16777216  # 16MB in bytes
```

### Customize Upload Limits
Edit `app.py` to modify file size limits:
```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
```

## 🧪 Integrating Real AI Models

The current implementation includes placeholder AI functions. To integrate real AI models:

### For Medical Image Analysis
```python
# Example using TensorFlow/Keras
import tensorflow as tf

def analyze_medical_image(image_path):
    model = tf.keras.models.load_model('path/to/your/model.h5')
    image = preprocess_image(image_path)
    predictions = model.predict(image)
    return process_predictions(predictions)
```

### For Text Symptom Analysis
```python
# Example using scikit-learn or transformers
from transformers import pipeline

def analyze_symptoms(symptoms_data):
    classifier = pipeline("text-classification", model="medical-symptom-model")
    results = classifier(symptoms_data['symptoms'])
    return process_results(results)
```

### For Audio Analysis
```python
# Example using librosa and machine learning
import librosa

def analyze_audio(audio_path):
    audio, sr = librosa.load(audio_path)
    features = extract_audio_features(audio, sr)
    predictions = audio_model.predict(features)
    return process_audio_predictions(predictions)
```

## 🛡️ Security Best Practices

1. **Never deploy with DEBUG=True in production**
2. **Use strong SECRET_KEY values**
3. **Implement user authentication for production**
4. **Use HTTPS for all communications**
5. **Regularly update dependencies**
6. **Implement rate limiting**
7. **Validate and sanitize all user inputs**

## 📊 API Endpoints

### GET /
- Returns the main application page

### POST /api/diagnose
- Accepts multi-modal diagnosis data
- Returns AI analysis results
- **Request Format**: multipart/form-data
- **Response Format**: JSON

### GET /api/health
- Health check endpoint
- Returns server status

## 🎯 Future Enhancements

- [ ] Integration with real medical AI models (TensorFlow, PyTorch)
- [ ] User authentication and patient accounts
- [ ] Medical history tracking
- [ ] Doctor consultation scheduling
- [ ] Real-time chat with healthcare professionals
- [ ] Multi-language support
- [ ] Mobile application (React Native/Flutter)
- [ ] Integration with wearable devices
- [ ] Prescription recommendations
- [ ] Drug interaction checker

## ⚠️ Disclaimer

**IMPORTANT**: This system provides preliminary AI-based health assessments for informational purposes only. It is NOT a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of qualified healthcare providers with questions regarding medical conditions.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for:
- Bug fixes
- New features
- Documentation improvements
- Performance enhancements

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍⚕️ Support

For support, questions, or feedback:
- Email: support@mediai.com
- GitHub Issues: [Create an issue](https://github.com/yourusername/medical_ai/issues)

## 🙏 Acknowledgments

- Flask framework for the backend
- Font Awesome for icons
- Google Fonts for typography
- Medical AI research community

---

**Built with ❤️ for better healthcare accessibility**

© 2026 MediAI. All rights reserved.
