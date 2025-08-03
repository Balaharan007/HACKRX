from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

from document_processor_v2 import DocumentProcessor

load_dotenv()

app = FastAPI(
    title="HackRx 6.0 Document Intelligence Agent - Simplified",
    description="AI-powered document analysis system without database dependency",
    version="2.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != BEARER_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

# Initialize document processor
doc_processor = DocumentProcessor()

# In-memory storage for demo purposes
documents_storage = {}
queries_storage = []

# Pydantic models
class HackRxRequest(BaseModel):
    documents: str
    questions: List[str]

class HackRxResponse(BaseModel):
    answers: List[str]

@app.get("/")
async def root():
    return {
        "message": "HackRx 6.0 Document Intelligence Agent API - Simplified Version",
        "version": "2.1.0",
        "features": [
            "Document processing (PDF, DOCX, TXT)",
            "File upload support",
            "Semantic search with Pinecone",
            "AI-powered answers with Gemini",
            "HackRx compatible endpoints",
            "In-memory storage (no database required)"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "hackrx-document-agent", "version": "2.1.0"}

@app.post("/hackrx/run", response_model=HackRxResponse)
async def hackrx_run(
    request: HackRxRequest,
    token: str = Depends(verify_token)
):
    """
    Main HackRx endpoint for document analysis and question answering
    Handles documents via URL and processes multiple questions
    """
    try:
        # Check if document is already processed
        if request.documents not in documents_storage:
            # Process the document
            print(f"Processing new document: {request.documents}")
            result = doc_processor.process_document(request.documents)
            
            if not result["success"]:
                raise HTTPException(status_code=400, detail=f"Document processing failed: {result['error']}")
            
            # Store document in memory
            documents_storage[request.documents] = {
                "title": request.documents.split('/')[-1],
                "content": result["text"][:10000],  # Store first 10k chars
                "chunks": result["chunks"],
                "document_id": result["document_id"]
            }
            document_id = result["document_id"]
        else:
            document_id = documents_storage[request.documents]["document_id"]
            print(f"Using existing document: {request.documents}")
        
        # Process each question
        answers = []
        for i, question in enumerate(request.questions):
            print(f"Processing question {i+1}/{len(request.questions)}: {question[:100]}...")
            
            # Search for relevant chunks
            relevant_chunks = doc_processor.search_similar_chunks(
                query=question,
                document_id=document_id,
                top_k=5
            )
            
            # Generate answer
            result = doc_processor.generate_answer(question, relevant_chunks)
            answer = result["answer"]
            
            # Store query in memory
            queries_storage.append({
                "document_url": request.documents,
                "question": question,
                "answer": answer,
                "relevant_chunks": result["relevant_chunks"]
            })
            
            answers.append(answer)
        
        return HackRxResponse(answers=answers)
    
    except Exception as e:
        print(f"Error in hackrx_run: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/documents/upload-file")
async def upload_file(
    file: UploadFile = File(...),
    title: str = Form(""),
    token: str = Depends(verify_token)
):
    """Upload and process a document file (PDF, DOCX, TXT)"""
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        file_ext = file.filename.lower().split('.')[-1]
        if file_ext not in ['pdf', 'docx', 'doc', 'txt']:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF, DOCX, or TXT files.")
        
        # Read file content
        file_content = await file.read()
        
        # Create unique identifier for file
        file_identifier = f"file_{file.filename}_{len(file_content)}"
        
        # Check if document already exists
        if file_identifier in documents_storage:
            return {
                "success": True,
                "message": "Document already processed",
                "document_id": documents_storage[file_identifier]["document_id"],
                "chunks": documents_storage[file_identifier]["chunks"]
            }
        
        # Process document
        result = doc_processor.process_document(
            source="",
            is_file_path=False,
            file_content=file_content,
            filename=file.filename
        )
        
        if not result["success"]:
            return {
                "success": False,
                "message": "Document processing failed",
                "error": result["error"]
            }
        
        # Store in memory
        documents_storage[file_identifier] = {
            "title": title or file.filename,
            "content": result["text"][:10000],
            "chunks": result["chunks"],
            "document_id": result["document_id"],
            "filename": file.filename
        }
        
        return {
            "success": True,
            "message": "Document processed successfully",
            "document_id": result["document_id"],
            "chunks": result["chunks"]
        }
    
    except Exception as e:
        print(f"File upload error: {str(e)}")
        return {
            "success": False,
            "message": "File upload failed",
            "error": str(e)
        }

@app.post("/query")
async def query_document(
    request: dict,
    token: str = Depends(verify_token)
):
    """Query a specific document by URL or document ID"""
    try:
        document_url = request.get("document_url")
        document_id = request.get("document_id")
        question = request.get("question")
        
        if not question:
            raise HTTPException(status_code=400, detail="Question is required")
        
        # Find document
        doc_info = None
        target_doc_id = None
        
        if document_url and document_url in documents_storage:
            doc_info = documents_storage[document_url]
            target_doc_id = doc_info["document_id"]
        elif document_id:
            # Search by document_id
            for key, value in documents_storage.items():
                if value["document_id"] == document_id:
                    doc_info = value
                    target_doc_id = document_id
                    break
        
        if not doc_info:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Search for relevant chunks
        relevant_chunks = doc_processor.search_similar_chunks(
            query=question,
            document_id=target_doc_id,
            top_k=5
        )
        
        # Generate answer
        result = doc_processor.generate_answer(question, relevant_chunks)
        
        # Store query
        queries_storage.append({
            "document_id": target_doc_id,
            "question": question,
            "answer": result["answer"],
            "relevant_chunks": result["relevant_chunks"]
        })
        
        return {
            "answer": result["answer"],
            "relevant_chunks": result["relevant_chunks"],
            "reasoning": result.get("reasoning", ""),
            "document_title": doc_info["title"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
async def list_documents(token: str = Depends(verify_token)):
    """List all processed documents"""
    documents = []
    for key, doc in documents_storage.items():
        documents.append({
            "id": key,
            "url": key if key.startswith("http") else None,
            "title": doc["title"],
            "chunks": doc["chunks"],
            "document_id": doc["document_id"],
            "is_file_upload": not key.startswith("http")
        })
    return documents

@app.get("/stats")
async def get_stats(token: str = Depends(verify_token)):
    """Get system statistics"""
    total_docs = len(documents_storage)
    total_queries = len(queries_storage)
    
    # Count file uploads vs URL documents
    file_uploads = sum(1 for key in documents_storage.keys() if not key.startswith("http"))
    url_documents = total_docs - file_uploads
    
    return {
        "total_documents": total_docs,
        "total_queries": total_queries,
        "file_uploads": file_uploads,
        "url_documents": url_documents,
        "avg_queries_per_doc": round(total_queries / max(total_docs, 1), 2)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_simple:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=True
    )
