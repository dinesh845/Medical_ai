"""
Real LLM Integration for Medical Chatbot
Supports OpenAI GPT, with fallback to rule-based responses
"""

import os
from dotenv import load_dotenv
from medical_knowledge import medical_kb

# Load environment variables
load_dotenv()

# LLM Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-4o-mini')
LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', '0.7'))
LLM_MAX_TOKENS = int(os.getenv('LLM_MAX_TOKENS', '800'))

# Try to import OpenAI
try:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
    OPENAI_AVAILABLE = client is not None
except ImportError:
    OPENAI_AVAILABLE = False
    client = None

# Medical AI System Prompt
MEDICAL_SYSTEM_PROMPT = """You are an AI Medical Assistant providing accurate, evidence-based health information. 

**Your Role:**
- Provide clear, accurate medical information based on current medical knowledge
- Use professional but friendly, empathetic tone
- Always include appropriate disclaimers
- Detect emergencies and urge immediate action

**Critical Rules:**
1. **Emergency Detection**: If user mentions chest pain, difficulty breathing, severe bleeding, stroke symptoms, or suicidal thoughts, IMMEDIATELY tell them to call 911 or emergency services
2. **No Diagnosis**: Never provide definitive diagnoses - only general information
3. **Encourage Professional Care**: Always recommend consulting healthcare providers for medical decisions
4. **Evidence-Based**: Provide medically accurate information
5. **Disclaimers**: Include "This is general information, not medical advice" when appropriate

**Response Format:**
- Use clear headings with **bold** text
- Numbered lists for steps/instructions
- Bullet points for multiple items
- Include "When to See a Doctor" sections
- Suggest follow-up questions when helpful

**Crisis Resources:**
- Suicide & Crisis: 988 (US)
- Emergency: 911
- Crisis Text Line: Text HOME to 741741

**Example Topics You Cover:**
- Symptoms (fever, headache, cough, pain)
- Conditions (colds, flu, infections)
- Mental health (anxiety, depression, stress)
- First aid and home care
- Prevention and wellness
- Medication information (general)

Remember: Your goal is to educate and guide, not diagnose or treat. Be helpful but always prioritize safety."""

class MedicalLLMChat:
    """Medical chatbot with LLM integration"""
    
    def __init__(self):
        self.use_openai = OPENAI_AVAILABLE
        self.conversation_history = []
    
    def get_response(self, user_message, chat_history=None):
        """Get chatbot response - uses OpenAI if available, otherwise fallback"""
        
        # Check for emergencies first (always do this)
        if medical_kb.detect_emergency(user_message):
            return medical_kb._emergency_response()
        
        # Try OpenAI first
        if self.use_openai:
            try:
                response = self._get_openai_response(user_message, chat_history)
                return response
            except Exception as e:
                print(f"OpenAI API error: {e}")
                # Fall back to rule-based
                return self._fallback_response(user_message)
        else:
            # Use rule-based knowledge base
            return self._fallback_response(user_message)
    
    def _get_openai_response(self, user_message, chat_history=None):
        """Get response from OpenAI GPT"""
        
        # Build conversation messages
        messages = [
            {"role": "system", "content": MEDICAL_SYSTEM_PROMPT}
        ]
        
        # Add chat history if provided
        if chat_history:
            for msg in chat_history[-6:]:  # Last 6 messages for context
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS
        )
        
        # Extract response
        bot_message = response.choices[0].message.content
        
        # Generate relevant suggestions based on message
        suggestions = self._generate_suggestions(user_message, bot_message)
        
        return {
            'message': bot_message,
            'suggestions': suggestions,
            'llm_used': 'openai'
        }
    
    def _fallback_response(self, user_message):
        """Fallback to rule-based medical knowledge base"""
        response = medical_kb.get_response(user_message)
        response['llm_used'] = 'knowledge_base'
        return response
    
    def _generate_suggestions(self, user_message, bot_response):
        """Generate relevant follow-up suggestions"""
        
        message_lower = user_message.lower()
        
        # Emergency-related
        if any(word in message_lower for word in ['chest', 'pain', 'breathe', 'bleeding']):
            return ['Call 911 now', 'Not an emergency', 'Other symptoms']
        
        # Symptom-related
        if any(word in message_lower for word in ['fever', 'headache', 'cough', 'hurt']):
            return ['How long to see doctor?', 'Home remedies', 'Is it serious?']
        
        # Mental health
        if any(word in message_lower for word in ['anxiety', 'stress', 'depressed', 'worried']):
            return ['Coping techniques', 'Find a therapist', 'Crisis support']
        
        # General health
        if any(word in message_lower for word in ['what', 'how', 'when', 'why']):
            return ['Tell me more', 'Prevention tips', 'When to see doctor']
        
        # Default suggestions
        return ['Ask another question', 'Different symptoms', 'Emergency info']

# Global chatbot instance
medical_llm_chat = MedicalLLMChat()

def get_chatbot_response(user_message, chat_history=None):
    """Main function to get chatbot response"""
    return medical_llm_chat.get_response(user_message, chat_history)
