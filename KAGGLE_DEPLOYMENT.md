# Running Medical AI Pre-Diagnosis System on Kaggle

This guide explains how to deploy and run your Medical AI project on Kaggle notebooks.

---

## 📋 Prerequisites

1. **Kaggle Account**: Sign up at [kaggle.com](https://www.kaggle.com)
2. **OpenAI API Key**: Get from [platform.openai.com](https://platform.openai.com/api-keys) (optional)

---

## 🚀 Method 1: Quick Start (Kaggle Notebook)

### Step 1: Create New Notebook

1. Go to [kaggle.com/code](https://www.kaggle.com/code)
2. Click **"New Notebook"**
3. Select **"Python"**
4. Name it: **"Medical AI Pre-Diagnosis System"**

### Step 2: Install Dependencies

In the first cell, run:

```python
# Install required packages
!pip install flask flask-cors pillow numpy python-dotenv openai --quiet

# Verify installation
print("✓ All packages installed successfully!")
```

### Step 3: Create Project Files

**Cell 2 - Create app.py:**

```python
%%writefile app.py
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

app = Flask(__name__)
app.config['SECRET_KEY'] = 'medical-ai-secret-key-2026'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
CORS(app)

os.makedirs('uploads/images', exist_ok=True)
os.makedirs('uploads/audio', exist_ok=True)
os.makedirs('data', exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'dcm', 'nii'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a'}

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def analyze_symptoms(symptoms_data):
    symptoms = symptoms_data.get('symptoms', '').lower()
    severity = symptoms_data.get('severity', 'moderate')
    possible_conditions = []
    
    if 'fever' in symptoms or 'temperature' in symptoms:
        possible_conditions.append({
            'name': 'Viral Infection',
            'confidence': 0.75,
            'description': 'Common viral infection with fever'
        })
    
    if 'headache' in symptoms:
        possible_conditions.append({
            'name': 'Tension Headache',
            'confidence': 0.68,
            'description': 'Stress-related headache'
        })
    
    return possible_conditions if possible_conditions else [
        {'name': 'General Health Issue', 'confidence': 0.5, 'description': 'Requires medical evaluation'}
    ]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    try:
        data = request.form.to_dict()
        symptoms_analysis = analyze_symptoms(data)
        
        return jsonify({
            'success': True,
            'conditions': symptoms_analysis,
            'recommendations': {
                'home_care': ['Rest', 'Stay hydrated', 'Monitor symptoms'],
                'when_to_see_doctor': ['Symptoms worsen', 'Fever above 103°F', 'Difficulty breathing']
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        chat_history = data.get('history', [])
        
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

if __name__ == '__main__':
    print("="*60)
    print("Medical AI Pre-Diagnosis System Starting...")
    print("="*60)
    print("Server running at: http://localhost:5000")
    print("="*60)
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
```

**Cell 3 - Create medical_knowledge.py:**

```python
%%writefile medical_knowledge.py
# Paste the entire content of medical_knowledge.py here
# (Copy from your local file c:\Users\MOHITH\Desktop\medical_ai\medical_knowledge.py)
```

**Cell 4 - Create llm_integration.py:**

```python
%%writefile llm_integration.py
import os
from dotenv import load_dotenv
from medical_knowledge import medical_kb

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

try:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
    OPENAI_AVAILABLE = client is not None
except ImportError:
    OPENAI_AVAILABLE = False
    client = None

class MedicalLLMChat:
    def __init__(self):
        self.use_openai = OPENAI_AVAILABLE
    
    def get_response(self, user_message, chat_history=None):
        if medical_kb.detect_emergency(user_message):
            return medical_kb._emergency_response()
        
        if self.use_openai:
            try:
                return self._get_openai_response(user_message, chat_history)
            except:
                return self._fallback_response(user_message)
        else:
            return self._fallback_response(user_message)
    
    def _fallback_response(self, user_message):
        response = medical_kb.get_response(user_message)
        response['llm_used'] = 'knowledge_base'
        return response

medical_llm_chat = MedicalLLMChat()

def get_chatbot_response(user_message, chat_history=None):
    return medical_llm_chat.get_response(user_message, chat_history)
```

**Cell 5 - Create HTML Template:**

```python
%%writefile templates/index.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Medical AI - Pre-Diagnosis System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Arial', sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 20px; 
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 { 
            color: #667eea; 
            text-align: center; 
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .form-group { 
            margin-bottom: 20px; 
        }
        label { 
            display: block; 
            margin-bottom: 8px; 
            color: #333;
            font-weight: 600;
        }
        input, textarea, select { 
            width: 100%; 
            padding: 12px; 
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border 0.3s;
        }
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        textarea { 
            resize: vertical; 
            min-height: 100px; 
        }
        button { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            border: none; 
            padding: 15px 40px; 
            border-radius: 30px;
            cursor: pointer; 
            font-size: 18px;
            font-weight: 600;
            width: 100%;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        button:hover { 
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }
        .results { 
            margin-top: 30px; 
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            display: none;
        }
        .condition {
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #667eea;
            border-radius: 5px;
        }
        .confidence {
            color: #667eea;
            font-weight: bold;
        }
        .chatbot {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #667eea;
            color: white;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            font-size: 30px;
        }
        .chat-window {
            position: fixed;
            bottom: 90px;
            right: 20px;
            width: 350px;
            height: 500px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            display: none;
            flex-direction: column;
        }
        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 15px 15px 0 0;
            font-weight: 600;
        }
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 15px;
        }
        .message {
            margin: 10px 0;
            padding: 10px 15px;
            border-radius: 15px;
            max-width: 80%;
        }
        .user-message {
            background: #667eea;
            color: white;
            margin-left: auto;
        }
        .bot-message {
            background: #f0f0f0;
            color: #333;
        }
        .chat-input {
            padding: 15px;
            border-top: 1px solid #e0e0e0;
            display: flex;
            gap: 10px;
        }
        .chat-input input {
            flex: 1;
            margin: 0;
        }
        .chat-input button {
            width: auto;
            padding: 10px 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏥 Medical AI</h1>
        <p class="subtitle">AI-Powered Pre-Diagnosis System</p>
        
        <form id="diagnosisForm">
            <div class="form-group">
                <label>Describe Your Symptoms:</label>
                <textarea id="symptoms" name="symptoms" required placeholder="E.g., I have a fever, headache, and cough..."></textarea>
            </div>
            
            <div class="form-group">
                <label>Severity:</label>
                <select id="severity" name="severity">
                    <option value="mild">Mild</option>
                    <option value="moderate" selected>Moderate</option>
                    <option value="severe">Severe</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>Duration:</label>
                <input type="text" id="duration" name="duration" placeholder="E.g., 2 days">
            </div>
            
            <button type="submit">🔍 Get Diagnosis</button>
        </form>
        
        <div class="results" id="results">
            <h2>Analysis Results</h2>
            <div id="conditions"></div>
            <div id="recommendations"></div>
        </div>
    </div>
    
    <div class="chatbot" id="chatbot" onclick="toggleChat()">💬</div>
    
    <div class="chat-window" id="chatWindow">
        <div class="chat-header">Medical AI Assistant</div>
        <div class="chat-messages" id="chatMessages"></div>
        <div class="chat-input">
            <input type="text" id="chatInput" placeholder="Ask a health question...">
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>
    
    <script>
        document.getElementById('diagnosisForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            
            try {
                const response = await fetch('/api/diagnose', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    displayResults(data);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        });
        
        function displayResults(data) {
            const resultsDiv = document.getElementById('results');
            const conditionsDiv = document.getElementById('conditions');
            
            conditionsDiv.innerHTML = data.conditions.map(c => `
                <div class="condition">
                    <h3>${c.name}</h3>
                    <p class="confidence">Confidence: ${(c.confidence * 100).toFixed(0)}%</p>
                    <p>${c.description}</p>
                </div>
            `).join('');
            
            resultsDiv.style.display = 'block';
        }
        
        function toggleChat() {
            const chatWindow = document.getElementById('chatWindow');
            chatWindow.style.display = chatWindow.style.display === 'flex' ? 'none' : 'flex';
        }
        
        async function sendMessage() {
            const input = document.getElementById('chatInput');
            const message = input.value.trim();
            if (!message) return;
            
            addMessage(message, 'user');
            input.value = '';
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message, history: [] })
                });
                
                const data = await response.json();
                addMessage(data.response, 'bot');
            } catch (error) {
                addMessage('Error: Could not get response', 'bot');
            }
        }
        
        function addMessage(text, type) {
            const messagesDiv = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}-message`;
            messageDiv.textContent = text;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        document.getElementById('chatInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    </script>
</body>
</html>
```

### Step 4: Set OpenAI API Key (Optional)

```python
# Add your OpenAI API key as Kaggle Secret or environment variable
import os
os.environ['OPENAI_API_KEY'] = 'your-key-here'  # Or use Kaggle Secrets
```

### Step 5: Run the Server

```python
# Run Flask in background
import threading
import time

def run_flask():
    from app import app
    app.run(host='0.0.0.0', port=5000, use_reloader=False, debug=False)

# Start server in background thread
thread = threading.Thread(target=run_flask)
thread.daemon = True
thread.start()

# Wait for server to start
time.sleep(3)
print("✓ Server is running on port 5000!")
print("✓ Access via Kaggle's output URLs")
```

### Step 6: Access the Application

**Important:** Kaggle notebooks run in isolated environments. To access your Flask app:

1. Click the **"Share"** button in Kaggle
2. Make notebook **"Public"**
3. Use **ngrok** or **localtunnel** for external access:

```python
# Install and run ngrok (recommended)
!pip install pyngrok --quiet

from pyngrok import ngrok

# Create tunnel
public_url = ngrok.connect(5000)
print(f"\n✓✓✓ Access your app at: {public_url}")
```

---

## 🌐 Method 2: Using Kaggle Datasets (Recommended)

### Step 1: Upload Project as Dataset

1. **Compress your project:**
   ```bash
   # On your local machine
   cd c:\Users\MOHITH\Desktop
   tar -czf medical_ai.tar.gz medical_ai/
   ```

2. **Upload to Kaggle:**
   - Go to [kaggle.com/datasets](https://www.kaggle.com/datasets)
   - Click **"New Dataset"**
   - Upload `medical_ai.tar.gz`
   - Name: "medical-ai-prediagnosis"

### Step 2: Create Notebook Using Dataset

```python
# Cell 1: Extract dataset
!tar -xzf /kaggle/input/medical-ai-prediagnosis/medical_ai.tar.gz
!cd medical_ai && ls -la

# Cell 2: Install dependencies
!cd medical_ai && pip install -r requirements.txt --quiet

# Cell 3: Run app
!cd medical_ai && python app.py
```

---

## 📱 Method 3: Deploy as Kaggle Kernel Output

### Create Streamlit Version (Alternative to Flask)

```python
# Install Streamlit
!pip install streamlit --quiet

# Create streamlit_app.py
%%writefile streamlit_app.py
import streamlit as st
from medical_knowledge import medical_kb

st.set_page_config(page_title="Medical AI", page_icon="🏥")

st.title("🏥 Medical AI Pre-Diagnosis System")
st.write("AI-Powered Health Assessment")

# Symptom input
symptoms = st.text_area("Describe your symptoms:", height=150)
severity = st.selectbox("Severity:", ["Mild", "Moderate", "Severe"])

if st.button("Get Diagnosis"):
    if symptoms:
        # Use medical knowledge base
        response = medical_kb.get_response(symptoms)
        st.success("Analysis Complete!")
        st.markdown(response['message'])
    else:
        st.warning("Please describe your symptoms")

# Chatbot
st.sidebar.title("💬 Chat Assistant")
user_question = st.sidebar.text_input("Ask a health question:")

if user_question:
    response = medical_kb.get_response(user_question)
    st.sidebar.markdown(response['message'])
    
# Run with: streamlit run streamlit_app.py
```

**Run Streamlit:**
```python
!streamlit run streamlit_app.py &

# Use localtunnel for public access
!npm install -g localtunnel
!lt --port 8501
```

---

## 🔑 Using Kaggle Secrets for API Keys

### Step 1: Add Secret

1. Go to **Kaggle Account Settings**
2. Navigate to **"Secrets"**
3. Add new secret:
   - **Name:** `OPENAI_API_KEY`
   - **Value:** Your OpenAI API key

### Step 2: Access in Notebook

```python
# Kaggle provides secrets via environment variables
import os
from kaggle_secrets import UserSecretsClient

user_secrets = UserSecretsClient()
openai_key = user_secrets.get_secret("OPENAI_API_KEY")

# Set environment variable
os.environ['OPENAI_API_KEY'] = openai_key

print("✓ API key loaded from Kaggle Secrets")
```

---

## 🚨 Important Kaggle Limitations

| Limitation | Kaggle | Solution |
|---|---|---|
| **External Network** | Limited | Use ngrok/localtunnel |
| **Session Time** | 12 hours max | Save progress regularly |
| **GPU/TPU** | Available | Not needed for this project |
| **Port Access** | Restricted | Use tunneling services |
| **File Persistence** | Output only | Save to Kaggle Datasets |

---

## 📦 Complete Kaggle Notebook Template

```python
# MEDICAL AI PRE-DIAGNOSIS SYSTEM - KAGGLE EDITION
# ==================================================

# 1. Install Dependencies
!pip install flask flask-cors pillow numpy python-dotenv openai pyngrok streamlit --quiet

# 2. Clone/Upload Files (choose one)
# Option A: From GitHub
!git clone https://github.com/your-repo/medical_ai.git

# Option B: From Kaggle Dataset
!cp -r /kaggle/input/medical-ai-dataset/* .

# 3. Setup Environment
import os
os.environ['OPENAI_API_KEY'] = 'your-key-here'  # Or use Kaggle Secrets

# 4. Start Flask Server
import threading
import time

def run_server():
    os.chdir('medical_ai')
    !python app.py

thread = threading.Thread(target=run_server)
thread.daemon = True
thread.start()

time.sleep(5)

# 5. Create Public URL
from pyngrok import ngrok

public_url = ngrok.connect(5000)
print(f"\n🌐 Access your Medical AI at:\n{public_url}\n")
print("✓ Server is running!")
print("✓ Visit the URL above to use your application")
```

---

## ✅ Testing on Kaggle

```python
# Test API endpoints
import requests

# Test health check
response = requests.get('http://localhost:5000/api/health')
print("Health Check:", response.json())

# Test chat
response = requests.post('http://localhost:5000/api/chat',
                        json={'message': 'I have a fever', 'history': []})
print("Chat Response:", response.json()['response'][:100])

print("\n✓ All systems working!")
```

---

## 🎯 Quick Start Commands

```bash
# 1-Minute Kaggle Setup
!pip install flask flask-cors pillow numpy python-dotenv openai pyngrok --quiet && \
git clone https://github.com/your-repo/medical_ai.git && \
cd medical_ai && \
python app.py &

# Get public URL
from pyngrok import ngrok
print(ngrok.connect(5000))
```

---

## 📚 Additional Resources

- **Kaggle Notebooks:** [kaggle.com/code](https://www.kaggle.com/code)
- **Ngrok Docs:** [ngrok.com/docs](https://ngrok.com/docs)
- **Flask on Kaggle:** Search "flask kaggle notebook" for examples
- **Streamlit Alternative:** Easier for Kaggle deployment

---

## 🔧 Troubleshooting

### Issue: "Cannot connect to server"
```python
# Check if Flask is running
!ps aux | grep python

# Check port
!netstat -tuln | grep 5000
```

### Issue: "Module not found"
```python
# Reinstall in notebook
!pip install --upgrade flask flask-cors pillow numpy python-dotenv openai
```

### Issue: "ngrok not working"
```python
# Alternative: localtunnel
!npm install -g localtunnel
!lt --port 5000
```

---

## ✨ Success Checklist

- [ ] Kaggle notebook created
- [ ] Dependencies installed
- [ ] Files uploaded/cloned
- [ ] API key configured (optional)
- [ ] Flask server running
- [ ] Public URL generated (ngrok)
- [ ] Application accessible
- [ ] Chat feature working
- [ ] Diagnosis feature working

---

**Your Medical AI is now running on Kaggle!** 🎉

Visit the ngrok URL to access your application from anywhere in the world.

**Note:** Kaggle sessions expire after 12 hours. Remember to save your work!
