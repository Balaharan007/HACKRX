# 🚀 HackRx 6.0 Document Intelligence Agent - Running Guide

## 📋 Quick Start (Both servers are already running!)

### ✅ Status Check

- **Backend API**: ✅ Running on http://localhost:8000
- **Streamlit UI**: ✅ Starting on http://localhost:8501

## 🔧 How to Run the Application

### Method 1: Complete Setup (Both Backend + UI)

1. **Start Backend API Server**:

```powershell
cd "c:\Users\haran\OneDrive\Desktop\final"
python main_final.py
```

2. **Start Streamlit UI** (in new terminal):

```powershell
cd "c:\Users\haran\OneDrive\Desktop\final"
streamlit run streamlit_app_v2.py --server.port 8501
```

### Method 2: API Only (for HackRx submission)

```powershell
cd "c:\Users\haran\OneDrive\Desktop\final"
python main_final.py
```

### Method 3: Using Uvicorn (Production)

```powershell
cd "c:\Users\haran\OneDrive\Desktop\final"
uvicorn main_final:app --host 0.0.0.0 --port 8000 --reload
```

## 🌐 Access Points

### 1. **Streamlit Web UI** (Recommended for Testing)

- **URL**: http://localhost:8501
- **Features**:
  - 📄 File upload (PDF, DOCX, TXT)
  - ❓ Interactive Q&A
  - 📊 Document statistics
  - 🔍 HackRx API testing

### 2. **FastAPI Backend**

- **URL**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🧪 Testing Your Document (Resume)

### Option A: Using Streamlit UI

1. Open http://localhost:8501
2. Go to "📄 Document Upload" page
3. Upload your `MAHENDRAVIKAS_RESUME.pdf`
4. Ask questions like:
   - "What are the key skills mentioned?"
   - "What is the work experience?"
   - "What education background is mentioned?"

### Option B: Using API Directly

```powershell
# Test with your resume
python -c "
import requests

# Upload file
files = {'file': open('MAHENDRAVIKAS_RESUME.pdf', 'rb')}
headers = {'Authorization': 'Bearer 96551ec397634df93a1a2212b9b798324340321ef3c785ce9f4593c92d8f1544'}

upload_resp = requests.post('http://localhost:8000/documents/upload-file', headers=headers, files=files)
print('Upload:', upload_resp.json())

# Query the document
query_data = {
    'question': 'What are the key skills of this person?',
    'document_id': upload_resp.json()['document_id']
}
headers['Content-Type'] = 'application/json'
query_resp = requests.post('http://localhost:8000/query', headers=headers, json=query_data)
print('Answer:', query_resp.json()['answer'])
"
```

## 🎯 HackRx API Testing

### Test with Official HackRx Endpoint

```powershell
python -c "
import requests
import json

headers = {
    'Authorization': 'Bearer 96551ec397634df93a1a2212b9b798324340321ef3c785ce9f4593c92d8f1544',
    'Content-Type': 'application/json'
}

# HackRx format
data = {
    'documents': 'This is a sample insurance policy. Coverage includes medical expenses up to $100,000. Premium is $500 annually.',
    'questions': [
        'What type of insurance is this?',
        'What is the coverage amount?',
        'What is the annual premium?'
    ]
}

response = requests.post('http://localhost:8000/hackrx/run', headers=headers, json=data)
print('HackRx Response:', response.json())
"
```

## 📊 Available Endpoints

| Endpoint                 | Method | Purpose                  |
| ------------------------ | ------ | ------------------------ |
| `/`                      | GET    | Service information      |
| `/health`                | GET    | Health check             |
| `/stats`                 | GET    | System statistics        |
| `/hackrx/run`            | POST   | **Main HackRx endpoint** |
| `/documents/upload-file` | POST   | Upload documents         |
| `/query`                 | POST   | Query documents          |
| `/docs`                  | GET    | Swagger documentation    |

## 🔐 Authentication

All endpoints require Bearer token:

```
Authorization: Bearer 96551ec397634df93a1a2212b9b798324340321ef3c785ce9f4593c92d8f1544
```

## 🛠 Troubleshooting

### If Backend Won't Start:

```powershell
# Check if port is in use
netstat -ano | findstr :8000

# Install dependencies
pip install -r requirements.txt

# Check environment variables
python -c "import os; print('GEMINI_API_KEY:', os.getenv('GEMINI_API_KEY')[:10]+'...' if os.getenv('GEMINI_API_KEY') else 'Missing')"
```

### If Streamlit Won't Start:

```powershell
# Try different port
streamlit run streamlit_app_v2.py --server.port 8502

# Check Streamlit installation
streamlit --version
```

## 🎉 Ready for HackRx 6.0!

Your application is now ready for the HackRx 6.0 competition with:

- ✅ Document processing (PDF, DOCX, TXT)
- ✅ AI-powered Q&A with Gemini
- ✅ HackRx API compliance
- ✅ File upload support
- ✅ Semantic search
- ✅ Explainable answers
- ✅ Multi-domain support (Insurance, Legal, HR, Compliance)

## 📞 Quick Commands Summary

```powershell
# Start everything (recommended)
cd "c:\Users\haran\OneDrive\Desktop\final"

# Terminal 1: Backend
python main_final.py

# Terminal 2: Frontend
streamlit run streamlit_app_v2.py

# Then open:
# - UI: http://localhost:8501
# - API: http://localhost:8000
# - Docs: http://localhost:8000/docs
```
