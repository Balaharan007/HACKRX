from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from database import get_db, Document, Query
from document_processor import DocumentProcessor

load_dotenv()

app = FastAPI(
    title="HackRx 6.0 Document Intelligence Agent",
    description="AI-powered document analysis and query system",
    version="1.0.0"
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
    document_url: str
    question: str

@app.get("/")
async def root():
    return {"message": "HackRx 6.0 Document Intelligence Agent API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "hackrx-document-agent"}

@app.post("/hackrx/run", response_model=HackRxResponse)
async def hackrx_run(
    request: HackRxRequest,
    token: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Main HackRx endpoint for document analysis and question answering
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
                content=result["text"],
                chunks={"count": result["chunks"]}
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)
            document_id = doc.id
        else:
            document_id = existing_doc.id
            print(f"Using existing document: {request.documents}")
        
        # Process each question
        answers = []
        for question in request.questions:
            print(f"Processing question: {question[:100]}...")
            
            # Search for relevant chunks
            relevant_chunks = doc_processor.search_similar_chunks(
                query=question,
                document_url=request.documents,
                top_k=5
            )
            
            # Generate answer
            result = doc_processor.generate_answer(question, relevant_chunks)
            answer = result["answer"]
            
            # Store query in database
            query_record = Query(
                document_id=document_id,
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

@app.post("/documents/upload")
async def upload_document(
    request: DocumentUploadRequest,
    token: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Upload and process a document"""
    try:
        # Check if document already exists
        existing_doc = db.query(Document).filter(Document.url == request.url).first()
        if existing_doc:
            return {"message": "Document already processed", "document_id": existing_doc.id}
        
        # Process document
        result = doc_processor.process_document(request.url)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Store in database
        doc = Document(
            url=request.url,
            title=request.title or request.url.split('/')[-1],
            content=result["text"],
            chunks={"count": result["chunks"]}
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        return {
            "message": "Document processed successfully",
            "document_id": doc.id,
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
    """Query a specific document"""
    try:
        # Find document
        doc = db.query(Document).filter(Document.url == request.document_url).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Search for relevant chunks
        relevant_chunks = doc_processor.search_similar_chunks(
            query=request.question,
            document_url=request.document_url,
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
            "relevant_chunks": result["relevant_chunks"]
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
            "chunks": doc.chunks
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
            "created_at": query.created_at
        }
        for query in queries
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=True
    )
