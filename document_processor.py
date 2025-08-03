import os
import requests
import PyPDF2
import docx
from io import BytesIO
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import pinecone
from pinecone import Pinecone
import google.generativeai as genai
from dotenv import load_dotenv
import hashlib
import json
import re

load_dotenv()

class DocumentProcessor:
    def __init__(self):
        # Initialize Pinecone
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index_name = "hackrx-documents"
        
        # Create index if it doesn't exist
        try:
            self.index = self.pc.Index(self.index_name)
        except:
            self.pc.create_index(
                name=self.index_name,
                dimension=384,  # for all-MiniLM-L6-v2
                metric="cosine",
                spec=pinecone.ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            self.index = self.pc.Index(self.index_name)
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize Gemini
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def download_document(self, url: str) -> bytes:
        """Download document from URL"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.content
        except Exception as e:
            raise Exception(f"Failed to download document: {str(e)}")
    
    def extract_text_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF"""
        try:
            pdf_file = BytesIO(content)
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise Exception(f"Failed to extract PDF text: {str(e)}")
    
    def extract_text_from_docx(self, content: bytes) -> str:
        """Extract text from DOCX"""
        try:
            doc = docx.Document(BytesIO(content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise Exception(f"Failed to extract DOCX text: {str(e)}")
    
    def extract_text(self, url: str) -> str:
        """Extract text from document URL"""
        content = self.download_document(url)
        
        if url.lower().endswith('.pdf'):
            return self.extract_text_from_pdf(content)
        elif url.lower().endswith('.docx'):
            return self.extract_text_from_docx(content)
        else:
            # Try to decode as plain text
            try:
                return content.decode('utf-8')
            except:
                raise Exception("Unsupported document format")
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
        """Split text into chunks with metadata"""
        # Clean text
        text = re.sub(r'\s+', ' ', text).strip()
        
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Find the last sentence boundary within the chunk
            if end < len(text):
                # Look for sentence endings
                sentence_end = text.rfind('.', start, end)
                if sentence_end == -1:
                    sentence_end = text.rfind('!', start, end)
                if sentence_end == -1:
                    sentence_end = text.rfind('?', start, end)
                
                if sentence_end != -1 and sentence_end > start + chunk_size // 2:
                    end = sentence_end + 1
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunks.append({
                    "id": f"chunk_{chunk_id}",
                    "text": chunk_text,
                    "start_pos": start,
                    "end_pos": end
                })
                chunk_id += 1
            
            start = end - overlap
        
        return chunks
    
    def embed_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """Generate embeddings for chunks"""
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embedding_model.encode(texts)
        
        for i, chunk in enumerate(chunks):
            chunk["embedding"] = embeddings[i].tolist()
        
        return chunks
    
    def store_in_pinecone(self, chunks: List[Dict], document_url: str):
        """Store chunks in Pinecone"""
        doc_hash = hashlib.md5(document_url.encode()).hexdigest()
        
        vectors = []
        for chunk in chunks:
            vector_id = f"{doc_hash}_{chunk['id']}"
            vectors.append({
                "id": vector_id,
                "values": chunk["embedding"],
                "metadata": {
                    "document_url": document_url,
                    "chunk_id": chunk["id"],
                    "text": chunk["text"],
                    "start_pos": chunk["start_pos"],
                    "end_pos": chunk["end_pos"]
                }
            })
        
        # Upsert in batches
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch)
    
    def process_document(self, url: str) -> Dict:
        """Complete document processing pipeline"""
        try:
            # Extract text
            text = self.extract_text(url)
            
            # Chunk text
            chunks = self.chunk_text(text)
            
            # Generate embeddings
            chunks = self.embed_chunks(chunks)
            
            # Store in Pinecone
            self.store_in_pinecone(chunks, url)
            
            return {
                "success": True,
                "text": text,
                "chunks": len(chunks),
                "message": f"Successfully processed document with {len(chunks)} chunks"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_similar_chunks(self, query: str, document_url: str = None, top_k: int = 5) -> List[Dict]:
        """Search for similar chunks"""
        query_embedding = self.embedding_model.encode([query])[0].tolist()
        
        filter_dict = {}
        if document_url:
            doc_hash = hashlib.md5(document_url.encode()).hexdigest()
            filter_dict = {"document_url": document_url}
        
        search_response = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filter_dict if filter_dict else None
        )
        
        results = []
        for match in search_response.matches:
            results.append({
                "score": match.score,
                "text": match.metadata["text"],
                "chunk_id": match.metadata["chunk_id"],
                "document_url": match.metadata["document_url"]
            })
        
        return results
    
    def generate_answer(self, question: str, relevant_chunks: List[Dict]) -> Dict:
        """Generate answer using Gemini"""
        context = "\n\n".join([f"[Clause {chunk['chunk_id']}]: {chunk['text']}" for chunk in relevant_chunks])
        
        prompt = f"""
        You are an intelligent document analysis agent. Based on the following document clauses and user question, provide a comprehensive answer.

        DOCUMENT CLAUSES:
        {context}

        USER QUESTION:
        {question}

        INSTRUCTIONS:
        1. Analyze the relevant clauses carefully
        2. Provide a clear, accurate answer based ONLY on the document content
        3. If the document doesn't contain sufficient information, state that clearly
        4. Reference specific clauses when relevant
        5. Be precise and professional

        ANSWER:
        """
        
        try:
            response = self.gemini_model.generate_content(prompt)
            return {
                "answer": response.text,
                "relevant_chunks": relevant_chunks
            }
        except Exception as e:
            return {
                "answer": f"Error generating answer: {str(e)}",
                "relevant_chunks": relevant_chunks
            }
