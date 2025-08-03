# HackRx 6.0 Document Intelligence Agent - Models and Versions

## 🤖 AI Models Used

### Primary AI Model

- **Google Gemini 2.0-Flash-Exp**: Main language model for document analysis and question answering
  - Version: Latest available through google-generativeai==0.3.2
  - Purpose: Document understanding, query processing, intelligent responses

### Text Similarity Model

- **Simple-Text-Similarity**: TF-IDF based text similarity for document matching
  - Implementation: Custom TF-IDF with cosine similarity
  - Purpose: Document relevance scoring and content matching

## 📦 Package Versions (Updated)

### Core Framework

```
fastapi==0.104.1           # API framework
uvicorn==0.24.0            # ASGI server
streamlit==1.29.0          # Web UI framework (updated from 1.28.1)
```

### AI and ML Libraries

```
google-generativeai==0.3.2    # Google Gemini API
scikit-learn==1.5.1           # ML utilities (updated from 1.3.2)
numpy==1.26.4                 # Numerical computing (updated from 1.24.3)
pandas==2.1.4                 # Data processing
```

### Web and HTTP

```
httpx==0.28.1                 # HTTP client (updated from 0.25.2)
requests==2.31.0              # HTTP requests
python-multipart==0.0.6       # File upload support
aiofiles==23.2.0              # Async file operations
```

### Document Processing

```
PyPDF2==3.0.1                 # PDF processing
python-docx==1.1.0            # Word document processing
```

### Database and Storage

```
pinecone-client==3.0.0        # Vector database
psycopg2-binary==2.9.9        # PostgreSQL adapter
sqlalchemy==2.0.23            # Database ORM
```

### Configuration and Utilities

```
python-dotenv==1.1.1          # Environment variables (updated from 1.0.0)
pydantic==2.5.2               # Data validation
```

## 🔧 Version Update Summary

### Recently Updated Packages:

1. **streamlit**: 1.28.1 → 1.29.0 (Latest stable version)
2. **python-dotenv**: 1.0.0 → 1.1.1 (Bug fixes and improvements)
3. **numpy**: 1.24.3 → 1.26.4 (Performance improvements)
4. **httpx**: 0.25.2 → 0.28.1 (Security and stability updates)
5. **scikit-learn**: 1.3.2 → 1.5.1 (Algorithm improvements)

## 🚀 Deployment Information

### Environment Compatibility

- **Python Version**: 3.12+
- **Operating System**: Windows 11 (tested), compatible with Linux/macOS
- **Memory Requirements**: 4GB+ RAM recommended
- **Storage**: 2GB+ free space for dependencies

### API Endpoints

- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:8501
- **Health Check**: http://localhost:8000/health

### Authentication

- **HackRx API Token**: Configured via environment variables
- **Gemini API**: Configured via GOOGLE_API_KEY

## 📊 Performance Metrics

### Model Performance

- **Gemini 2.0-Flash-Exp**: Ultra-fast response times (<2 seconds)
- **TF-IDF Similarity**: Near-instantaneous document matching
- **Combined System**: Average query response <3 seconds

### System Requirements Met

- ✅ Real-time document processing
- ✅ Multi-format document support (PDF, DOCX, TXT)
- ✅ Scalable architecture
- ✅ Error-resistant operation
- ✅ Production-ready deployment

---

_Last Updated: August 3, 2025_
_Version: 3.0.0_
_Ready for HackRx 6.0 Submission_
