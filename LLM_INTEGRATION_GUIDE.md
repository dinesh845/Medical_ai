# Instructions for LLM Integration

## Current Setup
The chatbot is currently using a rule-based system with medical knowledge base responses.

## Integrating Real LLM Models

### Option 1: OpenAI GPT-4 (Recommended)
```python
pip install openai

# In app.py, add:
import openai
openai.api_key = 'your-api-key-here'

def generate_medical_chat_response(user_message, chat_history):
    messages = [
        {"role": "system", "content": "You are a helpful medical AI assistant. Provide accurate health information but always remind users to consult healthcare professionals."}
    ]
    
    for msg in chat_history[-5:]:  # Last 5 messages for context
        messages.append({"role": msg['role'], "content": msg['content']})
    
    messages.append({"role": "user", "content": user_message})
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )
    
    return {
        'message': response.choices[0].message.content,
        'suggestions': []  # Generate relevant suggestions
    }
```

### Option 2: Anthropic Claude
```python
pip install anthropic

# In app.py:
import anthropic

client = anthropic.Anthropic(api_key="your-api-key-here")

def generate_medical_chat_response(user_message, chat_history):
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=500,
        system="You are a helpful medical AI assistant...",
        messages=[
            {"role": "user", "content": user_message}
        ]
    )
    
    return {
        'message': message.content[0].text,
        'suggestions': []
    }
```

### Option 3: Google Gemini
```python
pip install google-generativeai

import google.generativeai as genai

genai.configure(api_key='your-api-key-here')
model = genai.GenerativeModel('gemini-pro')

def generate_medical_chat_response(user_message, chat_history):
    chat = model.start_chat(history=[])
    response = chat.send_message(user_message)
    
    return {
        'message': response.text,
        'suggestions': []
    }
```

### Option 4: Hugging Face (Free, Self-Hosted)
```python
pip install transformers torch

from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "microsoft/BioGPT"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

def generate_medical_chat_response(user_message, chat_history):
    inputs = tokenizer(user_message, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=200)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return {
        'message': response,
        'suggestions': []
    }
```

### Option 5: LangChain (Best for Complex Workflows)
```python
pip install langchain langchain-openai

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

llm = ChatOpenAI(temperature=0.7, model_name="gpt-4")
memory = ConversationBufferMemory()
conversation = ConversationChain(llm=llm, memory=memory)

def generate_medical_chat_response(user_message, chat_history):
    response = conversation.predict(input=user_message)
    return {
        'message': response,
        'suggestions': []
    }
```

## Security Best Practices

1. **Never hardcode API keys** - Use environment variables:
```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
```

2. **Add rate limiting** to prevent abuse
3. **Implement content filtering** for inappropriate queries
4. **Add cost monitoring** for paid APIs
5. **Store chat logs securely** for analysis and improvement

## Medical Compliance

⚠️ **Important Legal Considerations:**

1. **Add clear disclaimers** - "This is not medical advice"
2. **HIPAA Compliance** - If storing patient data
3. **Data Privacy** - Encrypt sensitive information
4. **Content Moderation** - Filter harmful advice
5. **Emergency Detection** - Route urgent cases to emergency services

## Example .env File
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
GEMINI_API_KEY=xxxxxxxxxxxxx
```

## Cost Estimates (per 1000 messages)

- OpenAI GPT-4: ~$0.30
- Anthropic Claude: ~$0.25
- Google Gemini: ~$0.10
- Hugging Face: Free (self-hosted)

## Recommended Approach

For production medical chatbot:
1. Use **OpenAI GPT-4** or **Anthropic Claude** for best quality
2. Implement **LangChain** for conversation management
3. Add **vector database** (Pinecone/Weaviate) for medical knowledge retrieval
4. Use **prompt engineering** for medical context
5. Add **content filters** for safety
6. Implement **logging and monitoring**

## Testing
```python
# Test the chatbot
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I have a fever", "history": []}'
```
