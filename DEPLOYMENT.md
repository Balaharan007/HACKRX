# Deployment Guide for HackRx 6.0 Document Intelligence Agent

## 🚀 Recommended Deployment Platform: **Render** (Free Tier)

Render is the best choice for this project because:

- ✅ Free tier available
- ✅ Built-in PostgreSQL
- ✅ Automatic HTTPS
- ✅ Easy GitHub integration
- ✅ Good for FastAPI applications

## 📋 Step-by-Step Deployment on Render

### 1. Prepare Your Code

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - HackRx 6.0 Document Agent"
   git branch -M main
   git remote add origin https://github.com/yourusername/hackrx-document-agent.git
   git push -u origin main
   ```

### 2. Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Connect your GitHub account

### 3. Deploy PostgreSQL Database

1. Click "New" → "PostgreSQL"
2. Configure:
   - **Name**: `hackrx-db`
   - **Database**: `hackrx_db`
   - **User**: `postgres`
   - **Region**: Choose closest to you
   - **Plan**: Free
3. Click "Create Database"
4. Note the database URL (Internal Database URL)

### 4. Deploy FastAPI Service

1. Click "New" → "Web Service"
2. Connect your GitHub repository
3. Configure:

   - **Name**: `hackrx-api`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Plan**: Free

4. **Environment Variables**:

   ```
   PINECONE_API_KEY=your_pinecone_api_key_here
   PINECONE_ENVIRONMENT=your_pinecone_environment_here
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-2.0-flash-exp
   HUGGINGFACE_API_KEY=your_huggingface_api_key_here
   DATABASE_URL=[Your Render PostgreSQL Internal URL]
   API_HOST=0.0.0.0
   API_PORT=10000
   BEARER_TOKEN=96551ec397634df93a1a2212b9b798324340321ef3c785ce9f4593c92d8f1544
   ```

5. Click "Create Web Service"

### 5. Deploy Streamlit Service (Optional)

1. Click "New" → "Web Service"
2. Connect same repository
3. Configure:

   - **Name**: `hackrx-streamlit`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run streamlit_app.py --server.port 10000 --server.address 0.0.0.0`
   - **Plan**: Free

4. Add same environment variables as above

### 6. Test Your Deployment

Your API will be available at:

- `https://hackrx-api.onrender.com/hackrx/run`
- `https://hackrx-api.onrender.com/docs` (API documentation)

Test with curl:

```bash
curl -X POST "https://hackrx-api.onrender.com/hackrx/run" \
  -H "Authorization: Bearer 96551ec397634df93a1a2212b9b798324340321ef3c785ce9f4593c92d8f1544" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": ["What is the grace period for premium payment?"]
  }'
```

## 🔄 Alternative Deployment Options

### Railway (Also Recommended)

1. **Pros**: Very simple, includes database, auto-deployment
2. **Cons**: Limited free tier
3. **Steps**:
   - Connect GitHub to Railway
   - Add PostgreSQL plugin
   - Set environment variables
   - Deploy automatically

### Heroku

1. **Pros**: Well-documented, reliable
2. **Cons**: Paid PostgreSQL, more complex
3. **Steps**:
   - Install Heroku CLI
   - `heroku create hackrx-api`
   - `heroku addons:create heroku-postgresql:mini`
   - `git push heroku main`

### Vercel (Serverless)

1. **Pros**: Fast, free functions
2. **Cons**: Cold starts, limited execution time
3. **Note**: Best for simple APIs, might timeout on document processing

### Self-Hosted VPS

1. **DigitalOcean**: $5/month droplet
2. **Linode**: $5/month VPS
3. **AWS EC2**: Free tier available

## 🔧 Production Optimizations

### 1. Environment Variables for Production

```env
# Production settings
DEBUG=false
DATABASE_POOL_SIZE=10
PINECONE_TIMEOUT=30
GEMINI_TIMEOUT=30
```

### 2. Performance Improvements

```python
# In document_processor.py
# Increase batch size for better performance
batch_size = 200  # Instead of 100

# In main.py
# Add request timeout
from fastapi import Request
import asyncio

@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    try:
        return await asyncio.wait_for(call_next(request), timeout=60.0)
    except asyncio.TimeoutError:
        return {"error": "Request timeout"}
```

### 3. Monitoring and Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add to main endpoints
logger.info(f"Processing document: {request.documents}")
logger.info(f"Questions count: {len(request.questions)}")
```

## 🛡️ Security Considerations

1. **API Key Security**: Never expose in logs
2. **HTTPS Only**: Ensure Render enables HTTPS
3. **Rate Limiting**: Consider adding rate limits
4. **Input Validation**: Validate all inputs

## 📊 Monitoring Your Deployment

1. **Render Dashboard**: Monitor CPU, memory, requests
2. **PostgreSQL Metrics**: Check database performance
3. **Pinecone Usage**: Monitor vector storage quota
4. **Gemini API**: Track API usage and costs

## 🔄 CI/CD Setup

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Render

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Render
        run: |
          curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}
```

## 📝 Final Checklist

- [ ] GitHub repository created and code pushed
- [ ] Render account created and connected to GitHub
- [ ] PostgreSQL database deployed and URL copied
- [ ] FastAPI service deployed with correct environment variables
- [ ] API endpoint tested with curl or Postman
- [ ] HackRx endpoint accessible via HTTPS
- [ ] Bearer token authentication working
- [ ] Document processing pipeline tested
- [ ] Response format matches HackRx requirements

## 🎯 Submit to HackRx

Your final API URL will be:

```
https://hackrx-api.onrender.com/hackrx/run
```

Submit this URL along with the bearer token for evaluation.

---

**Good luck with HackRx 6.0!** 🏆
