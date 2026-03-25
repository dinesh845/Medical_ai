# 🤖 Real LLM Integration Setup Guide

## Quick Setup (Choose Your Option)

### Option 1: Use OpenAI GPT (Recommended - Best Quality)

**✨ Why OpenAI?**
- Most reliable and accurate medical responses
- Fast response times
- GPT-4o-mini is cost-effective (~$0.15 per 1M tokens)

**Setup Steps:**

1. **Get Your API Key**
   - Go to https://platform.openai.com/api-keys
   - Sign up or log in
   - Click "Create new secret key"
   - Copy the key (starts with `sk-...`)

2. **Create `.env` file in project root**
   ```bash
   # Copy the example file
   copy .env.example .env
   ```

3. **Add Your API Key**
   Open `.env` and replace:
   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   LLM_MODEL=gpt-4o-mini
   LLM_TEMPERATURE=0.7
   LLM_MAX_TOKENS=800
   ```

4. **Run the Application**
   ```bash
   python app.py
   ```

**Cost Estimate:**
- GPT-4o-mini: ~$0.10-0.30 per day for moderate use
- GPT-4o: ~$1-3 per day (better quality)

---

### Option 2: Free Alternative (No API Key Needed)

**The chatbot will automatically use the built-in medical knowledge base:**
- ✅ 15+ medical topics covered
- ✅ Evidence-based information
- ✅ Emergency detection
- ✅ 100% free, no API needed

**Just run:**
```bash
python app.py
```

The system automatically detects if no API key is present and uses the comprehensive rule-based responses instead.

---

## Testing Your Setup

### Test 1: Check if LLM is Connected
```bash
python test_llm.py
```

### Test 2: Chat with the Bot
```bash
python
>>> from llm_integration import get_chatbot_response
>>> response = get_chatbot_response("I have a fever")
>>> print(response['message'])
>>> print(f"Using: {response['llm_used']}")
```

### Test 3: Via Web Interface
1. Start server: `python app.py`
2. Open: http://localhost:5000
3. Click chat icon (bottom right)
4. Ask: "I have a headache"

---

## Model Options

### OpenAI Models
```env
# Fast & Cheap (Recommended)
LLM_MODEL=gpt-4o-mini

# Best Quality
LLM_MODEL=gpt-4o

# Legacy (Cheaper)
LLM_MODEL=gpt-3.5-turbo
```

### Cost Comparison (per 1M tokens)
| Model | Input | Output | Quality |
|-------|-------|--------|---------|
| gpt-4o-mini | $0.15 | $0.60 | ⭐⭐⭐⭐ |
| gpt-4o | $2.50 | $10.00 | ⭐⭐⭐⭐⭐ |
| gpt-3.5-turbo | $0.50 | $1.50 | ⭐⭐⭐ |

**Real-world usage:**
- 100 chat messages ≈ 100,000 tokens
- With gpt-4o-mini: ~$0.10
- With gpt-4o: ~$1.50

---

## Settings Explained

```env
# Your OpenAI API key
OPENAI_API_KEY=sk-xxx

# Which model to use
LLM_MODEL=gpt-4o-mini

# Creativity (0.0-2.0)
# 0.7 = balanced, good for medical info
# 1.0 = more creative/varied responses
LLM_TEMPERATURE=0.7

# Maximum response length
# 800 = ~600 words
LLM_MAX_TOKENS=800
```

---

## Troubleshooting

### Error: "OpenAI API key not found"
**Solution:** Create `.env` file with your API key

### Error: "Rate limit exceeded"
**Solution:** 
- Wait a few minutes
- Upgrade your OpenAI plan
- System will auto-fallback to knowledge base

### Error: "Invalid API key"
**Solution:**
- Check key starts with `sk-`
- Regenerate key at platform.openai.com
- Verify no extra spaces in `.env` file

### Chatbot gives generic responses
**Check which LLM is being used:**
- Look at browser console or terminal logs
- Should say `"llm_used": "openai"` for GPT
- If says `"knowledge_base"`, API key not configured

---

## Advanced: Multiple LLM Support

Want to use Claude or Gemini instead? Edit `llm_integration.py`:

```python
# For Anthropic Claude
from anthropic import Anthropic
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# For Google Gemini
import google.generativeai as genai
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
```

---

## Security Best Practices

1. ✅ **Never commit `.env` file to git**
   - Already in `.gitignore`
   
2. ✅ **Rotate API keys regularly**
   - Change keys every 90 days
   
3. ✅ **Set usage limits**
   - Configure at platform.openai.com/usage
   - Set monthly budget alerts
   
4. ✅ **Monitor usage**
   - Check platform.openai.com/usage
   - Track costs daily

---

## What's the Difference?

### With OpenAI GPT:
- 🎯 Natural, conversational responses
- 🧠 Understands context and follow-ups
- 📚 Vast medical knowledge (trained on internet)
- 💬 Can explain complex topics simply
- ❓ Handles any health question

### Without (Knowledge Base Only):
- ✅ Still very comprehensive
- ✅ Covers common health topics
- ✅ Emergency detection works
- ✅ 100% free
- ⚠️ Limited to pre-programmed topics

---

## Need Help?

**Check system status:**
```bash
python -c "from llm_integration import OPENAI_AVAILABLE; print(f'OpenAI Available: {OPENAI_AVAILABLE}')"
```

**View detailed logs:**
- Start app and watch terminal
- Errors shown in red
- "llm_used" field shows which system answered

**Still having issues?**
- Check `.env` file exists
- Verify API key is correct
- Ensure openai package installed: `pip install openai`
- Restart the server

---

## Ready to Go!

**Your chatbot now provides real-world accurate answers using:**
1. 🤖 **OpenAI GPT** (if API key configured) - Natural, intelligent responses
2. 📚 **Medical Knowledge Base** (automatic fallback) - Comprehensive pre-programmed info
3. 🚨 **Emergency Detection** (always active) - Life-saving alerts

**Start chatting:**
```bash
python app.py
```
Then open http://localhost:5000 and click the chat icon! 💬
