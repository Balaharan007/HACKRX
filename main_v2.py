from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from database import get_db, Document, Query
from document_processor_v2 import DocumentProcessor

load_dotenv()

app = FastAPI(
    title="HackRx 6.0 Document Intelligence Agent",
    description="AI-powered document analysis and query system with file upload support",
    version="2.0.0"
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

# Pydantic models
class HackRxRequest(BaseModel):
    documents: str
    questions: List[str]

class HackRxResponse(BaseModel):
    answers: List[str]

class DocumentUploadRequest(BaseModel):
    url: str
    title: str = ""

class QueryRequest(BaseModel):
    document_url: Optional[str] = None
    document_id: Optional[str] = None
    question: str

class FileUploadResponse(BaseModel):
    success: bool
    message: str
    document_id: Optional[str] = None
    chunks: Optional[int] = None
    error: Optional[str] = None

@app.get("/")
async def root():
    return {
        "message": "HackRx 6.0 Document Intelligence Agent API",
        "version": "2.0.0",
        "features": [
            "Document processing (PDF, DOCX, TXT)",
            "File upload support",
            "Semantic search with Pinecone",
            "AI-powered answers with Gemini",
            "HackRx compatible endpoints"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "hackrx-document-agent", "version": "2.0.0"}

@app.post("/hackrx/run", response_model=HackRxResponse)
async def hackrx_run(
    request: HackRxRequest,
    token: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Main HackRx endpoint for document analysis and question answering
    Handles documents via URL and processes multiple questions
    """
    try:
        # Check if document is already processed
        existing_doc = db.query(Document).filter(Document.url == request.documents).first()
        
        if not existing_doc:
            # Process the document
            print(f"Processing new document: {request.documents}")
            result = doc_processor.process_document(request.documents)
            
            if not result["success"]:
                raise HTTPException(status_code=400, detail=f"Document processing failed: {result['error']}")
            
            # Store document in database
            doc = Document(
                url=request.documents,
                title=request.documents.split('/')[-1],
                content=result["text"][:10000],  # Store first 10k chars
                chunks={"count": result["chunks"], "document_id": result["document_id"]}
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)
            document_id = result["document_id"]
        else:
            document_id = existing_doc.chunks.get("document_id") if existing_doc.chunks else None
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
            
            # Store query in database
            query_record = Query(
                document_id=existing_doc.id if existing_doc else doc.id,
                question=question,
                answer=answer,
                justification=result["relevant_chunks"]
            )
            db.add(query_record)
            
            answers.append(answer)
        
        db.commit()
        
        return HackRxResponse(answers=answers)
    
    except Exception as e:
        print(f"Error in hackrx_run: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/documents/upload-file", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    title: str = Form(""),
    token: str = Depends(verify_token),
    db: Session = Depends(get_db)
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
        
        # Check if document already exists (based on filename and size)
        doc_identifier = f"{file.filename}_{len(file_content)}"
        existing_doc = db.query(Document).filter(Document.url == doc_identifier).first()
        
        if existing_doc:
            return FileUploadResponse(
                success=True,
                message="Document already processed",
                document_id=existing_doc.chunks.get("document_id") if existing_doc.chunks else None,
                chunks=existing_doc.chunks.get("count") if existing_doc.chunks else 0
            )
        
        # Process document
        result = doc_processor.process_document(
            source="",
            is_file_path=False,
            file_content=file_content,
            filename=file.filename
        )
        
        if not result["success"]:
            return FileUploadResponse(
                success=False,
                message="Document processing failed",
                error=result["error"]
            )
        
        # Store in database
        doc = Document(
            url=doc_identifier,
            title=title or file.filename,
            content=result["text"][:10000],  # Store first 10k chars
            chunks={"count": result["chunks"], "document_id": result["document_id"]}
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        return FileUploadResponse(
            success=True,
            message="Document processed successfully",
            document_id=result["document_id"],
            chunks=result["chunks"]
        )
    
    except Exception as e:
        print(f"File upload error: {str(e)}")
        return FileUploadResponse(
            success=False,
            message="File upload failed",
            error=str(e)
        )

@app.post("/documents/upload-url")
async def upload_document_url(
    request: DocumentUploadRequest,
    token: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Upload and process a document from URL"""
    try:
        # Check if document already exists
        existing_doc = db.query(Document).filter(Document.url == request.url).first()
        if existing_doc:
            return {
                "success": True,
                "message": "Document already processed",
                "document_id": existing_doc.chunks.get("document_id") if existing_doc.chunks else None,
                "chunks": existing_doc.chunks.get("count") if existing_doc.chunks else 0
            }
        
        # Process document
        result = doc_processor.process_document(request.url)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Store in database
        doc = Document(
            url=request.url,
            title=request.title or request.url.split('/')[-1],
            content=result["text"][:10000],  # Store first 10k chars
            chunks={"count": result["chunks"], "document_id": result["document_id"]}
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        return {
            "success": True,
            "message": "Document processed successfully",
            "document_id": result["document_id"],
            "chunks": result["chunks"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_document(
    request: QueryRequest,
    token: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Query a specific document by URL or document ID"""
    try:
        # Find document
        if request.document_url:
            doc = db.query(Document).filter(Document.url == request.document_url).first()
        elif request.document_id:
            doc = db.query(Document).filter(
                Document.chunks.op('->>')('document_id') == request.document_id
            ).first()
        else:
            raise HTTPException(status_code=400, detail="Either document_url or document_id must be provided")
        
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get document ID from chunks metadata
        document_id = doc.chunks.get("document_id") if doc.chunks else None
        
        # Search for relevant chunks
        relevant_chunks = doc_processor.search_similar_chunks(
            query=request.question,
            document_id=document_id,
            top_k=5
        )
        
        # Generate answer
        result = doc_processor.generate_answer(request.question, relevant_chunks)
        
        # Store query
        query_record = Query(
            document_id=doc.id,
            question=request.question,
            answer=result["answer"],
            justification=result["relevant_chunks"]
        )
        db.add(query_record)
        db.commit()
        
        return {
            "answer": result["answer"],
            "relevant_chunks": result["relevant_chunks"],
            "reasoning": result.get("reasoning", ""),
            "document_title": doc.title
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
async def list_documents(
    token: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """List all processed documents"""
    docs = db.query(Document).all()
    return [
        {
            "id": doc.id,
            "url": doc.url,
            "title": doc.title,
            "created_at": doc.created_at,
            "chunks": doc.chunks.get("count") if doc.chunks else 0,
            "document_id": doc.chunks.get("document_id") if doc.chunks else None,
            "is_file_upload": not doc.url.startswith("http")
        }
        for doc in docs
    ]

@app.get("/documents/{document_id}/queries")
async def get_document_queries(
    document_id: int,
    token: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get all queries for a document"""
    queries = db.query(Query).filter(Query.document_id == document_id).all()
    return [
        {
            "id": query.id,
            "question": query.question,
            "answer": query.answer,
            "created_at": query.created_at,
            "justification_count": len(query.justification) if query.justification else 0
        }
        for query in queries
    ]

@app.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    token: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Delete a document and its queries"""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete associated queries
    db.query(Query).filter(Query.document_id == document_id).delete()
    
    # Delete document
    db.delete(doc)
    db.commit()
    
    return {"message": "Document deleted successfully"}

@app.get("/stats")
async def get_stats(
    token: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get system statistics"""
    total_docs = db.query(Document).count()
    total_queries = db.query(Query).count()
    
    # Count file uploads vs URL documents
    docs = db.query(Document).all()
    file_uploads = sum(1 for doc in docs if not doc.url.startswith("http"))
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
        "main_v2:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=True
    )
