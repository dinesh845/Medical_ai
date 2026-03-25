# Uploading to Kaggle - Manual Instructions

## Quick Start: 2 Methods to Get Your Project on Kaggle

---

## Method 1: Upload Notebook Directly (Recommended & Fastest) ⭐

### Step-by-Step:

1. **Go to Kaggle Code**
   - Visit: https://www.kaggle.com/code
   - Click **"New Notebook"** (blue button, top right)

2. **Configure Notebook**
   - Name: `Medical AI Pre-Diagnosis System`
   - Language: Python
   - Notebook type: Notebook (not script)

3. **Upload the Notebook File**
   - Click **"File"** → **"Upload"**
   - Select: `Medical_AI_Kaggle.ipynb`
   - Or copy-paste the cells from the notebook

4. **Run & Test**
   - Click **"Run All"** to execute all cells
   - System will install dependencies automatically
   - Test API endpoints in the notebook

5. **Save & Publish**
   - Click **"Save Version"** (top right)
   - Select **"Make Public"** to share
   - Your notebook is now live!

---

## Method 2: Upload as Dataset (For Others to Use)

### Step-by-Step:

1. **Prepare Files**
   ```bash
   # Navigate to project folder
   cd c:\Users\MOHITH\Desktop\medical_ai
   ```

2. **Create Compressed Archive**
   ```powershell
   # Create zip on Windows
   Compress-Archive -Path * -DestinationPath medical_ai.zip -Exclude ".venv"
   ```

3. **Upload Dataset on Kaggle**
   - Go to: https://www.kaggle.com/datasets/create
   - Click **"Upload Files"**
   - Select `medical_ai.zip`
   - Add metadata:
     - **Title**: Medical AI Pre-Diagnosis System
     - **Description**: AI-powered pre-diagnosis with Flask, LLM, and chatbot
     - **License**: Creative Commons 0 v1 (CC0 1.0)
     - **Tags**: medical, ai, diagnosis, chatbot, flask, openai

4. **Make Public**
   - After uploading, select **"Make Public"**
   - Share dataset link with others

---

## Method 3: Using Kaggle API (Alternative)

If the direct upload doesn't work due to authentication issues:

1. **Verify Your API Key**
   - Sign in to: https://www.kaggle.com/settings/account
   - Click **"Create New Token"**
   - This downloads fresh `kaggle.json`

2. **Place Credentials**
   ```powershell
   Copy-Item "$env:USERPROFILE\Downloads\kaggle.json" -Destination "$env:USERPROFILE\.kaggle\kaggle.json" -Force
   ```

3. **Try Upload Again**
   ```powershell
   cd c:\Users\MOHITH\Desktop\medical_ai
   kaggle datasets create -p . --public --dir-mode zip
   ```

---

## What Gets Uploaded

Your notebook includes:

✅ Medical Knowledge Base (`medical_knowledge.py`)  
✅ Flask Application (`app.py`)  
✅ API Endpoints (Health, Chat, Diagnosis)  
✅ Emergency Detection System  
✅ Test Suite  
✅ LLM Integration Ready  

---

## Access After Upload

Once uploaded, your notebook will be available at:

```
https://www.kaggle.com/code/mohitherabbithula/medical-ai-prediagnosis-system
```

Or your dataset at:

```
https://www.kaggle.com/datasets/mohitherabbithula/medical-ai-prediagnosis
```

---

## Troubleshooting

### 401 Unauthorized Error
- Regenerate API key from Kaggle Settings
- Ensure `~/.kaggle/kaggle.json` is downloaded from Kaggle
- Verify username and key are correct

### Upload Fails
- Exclude large folders (`.venv`, `uploads`, `data`)
- Use `.kaggleignore` file (already created)
- Compress files manually first

### Can't Find Notebook
- Check **"Your Work"** → **"Code"** on Kaggle
- Search for "medical-ai" in Kaggle search

---

## Next Steps

After uploading:

1. ✨ **Share** your notebook with the community
2. 📊 **Enable Discussions** for collaboration
3. 🔗 **Link to GitHub** for full source code
4. 📈 **Monitor** usage and engagement
5. 🚀 **Iterate** based on feedback

---

**Your Medical AI is ready for Kaggle!** 🎉

