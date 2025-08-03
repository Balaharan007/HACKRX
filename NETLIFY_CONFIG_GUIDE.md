# Netlify Environment Variables Configuration

## 🔧 Required Environment Variables for Netlify

### Secret Variables (Check "Contains secret values" in Netlify):

```
GEMINI_API_KEY=[Your Google Gemini API Key]
PINECONE_API_KEY=[Your Pinecone API Key]  
HUGGINGFACE_API_KEY=[Your Hugging Face API Key]
BEARER_TOKEN=[Your Bearer Token from .env file]
```

### Public Variables:

```
GEMINI_MODEL=gemini-2.0-flash-exp
PINECONE_ENVIRONMENT=gcp-starter
PINECONE_INDEX_NAME=hackrx-documents
NODE_VERSION=18
```

## ❌ Variables to REMOVE from Netlify:

These are for local development only:
- `STREAMLIT_PORT=8501` (Not needed for serverless functions)
- `API_HOST=0.0.0.0` (Not needed for serverless functions)  
- `API_PORT=8000` (Not needed for serverless functions)
- Local database variables (Use production DATABASE_URL instead)

## ✅ Deploy Contexts:

Your current selection is correct:
- ✅ Production
- ✅ Deploy Previews  
- ✅ Branch deploys
- ✅ Local development (Netlify CLI)

## 📋 Step-by-Step Setup:

1. **Copy your actual API keys** from your local `.env` file
2. **Add them as secret variables** in Netlify dashboard
3. **Remove the unnecessary variables** listed above
4. **Keep your current deploy context settings**
5. **Deploy your application**

Your Netlify function configuration looks correct for the HackRx API!
