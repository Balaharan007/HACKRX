# 🚀 Complete GitHub + Netlify Deployment Guide

## 📦 **GitHub Upload Status**

- ✅ Repository created: https://github.com/Balaharan007/HACKRX
- 🔄 Files to upload manually (excluding .env with API keys)

## 📂 **Files to Upload to GitHub**

### ✅ **Core Application Files**

```
main_final.py              # Main FastAPI application
simple_processor.py        # Document processor
requirements.txt           # Python dependencies
.env.example              # Environment template
.gitignore                # Git ignore file
```

### ✅ **Netlify Deployment Files**

```
netlify/
  └── functions/
      └── hackrx.js         # Serverless function
package.json              # Node.js dependencies
netlify.toml             # Netlify configuration
```

### ✅ **Documentation & Config**

```
README.md
HACKRX_COMPLIANCE_ANALYSIS.md
NETLIFY_DEPLOYMENT.md
RUN_APPLICATION.md
docker-compose.yml
Dockerfile
```

### ❌ **DO NOT Upload**

```
.env                     # Contains API keys - NEVER upload
__pycache__/            # Python cache
*.log                   # Log files
```

---

## 🌐 **Netlify Deployment Steps**

### Step 1: Connect Repository

1. Go to https://netlify.com
2. Click "New site from Git"
3. Connect GitHub account
4. Select "Balaharan007/HACKRX" repository

### Step 2: Build Settings

```
Build command: npm install
Publish directory: (leave empty)
Functions directory: netlify/functions
```

### Step 3: Environment Variables

Add these in Netlify Dashboard → Site Settings → Environment Variables:

```bash
BEARER_TOKEN=96551ec397634df93a1a2212b9b798324340321ef3c785ce9f4593c92d8f1544
GEMINI_API_KEY=your_actual_gemini_key_here
HUGGINGFACE_API_KEY=your_actual_huggingface_key_here
PINECONE_API_KEY=your_actual_pinecone_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment_here
PINECONE_INDEX_NAME=hackrx-documents
```

### Step 4: Deploy

Click "Deploy site" - Netlify will:

- Install dependencies
- Build the function
- Deploy with HTTPS automatically

---

## 🎯 **Your HackRx API URL**

After deployment, your API will be available at:

```
https://your-site-name.netlify.app/hackrx/run
```

### Test Your Deployed API:

```bash
curl -X POST "https://your-site-name.netlify.app/hackrx/run" \
  -H "Authorization: Bearer 96551ec397634df93a1a2212b9b798324340321ef3c785ce9f4593c92d8f1544" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": ["What is the grace period for premium payment?"]
  }'
```

---

## ✅ **Final Checklist**

### GitHub Upload:

- [ ] Upload all files except .env
- [ ] Include .env.example for reference
- [ ] Verify netlify/ folder is uploaded
- [ ] Check package.json and netlify.toml are present

### Netlify Deployment:

- [ ] Connect GitHub repository
- [ ] Set build command to "npm install"
- [ ] Add all environment variables
- [ ] Deploy and test the /hackrx/run endpoint
- [ ] Verify HTTPS is enabled (automatic)
- [ ] Test with HackRx sample data

### HackRx Submission:

- [ ] API responds to POST /hackrx/run
- [ ] Bearer token authentication works
- [ ] Response format: {"answers": [...]}
- [ ] Response time < 30 seconds
- [ ] Public HTTPS URL ready

## 🏆 **You're Ready for HackRx 6.0!**

Your API URL: `https://your-site-name.netlify.app/hackrx/run`
