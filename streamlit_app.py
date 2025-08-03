import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

# Configuration
API_BASE_URL = f"http://localhost:{os.getenv('API_PORT', 8000)}"
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

st.set_page_config(
    page_title="HackRx 6.0 - Document Intelligence Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def make_api_request(endpoint: str, data: dict = None, method: str = "GET"):
    """Make API request with authentication"""
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            response = requests.get(url, headers=headers)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None

def main():
    st.title("🤖 HackRx 6.0 - Document Intelligence Agent")
    st.markdown("### AI-powered document analysis and query system")
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["HackRx API Test", "Document Upload", "Query Documents", "Document Management"]
    )
    
    if page == "HackRx API Test":
        hackrx_api_test()
    elif page == "Document Upload":
        document_upload_page()
    elif page == "Query Documents":
        query_documents_page()
    elif page == "Document Management":
        document_management_page()

def hackrx_api_test():
    """HackRx API test page"""
    st.header("🧪 HackRx API Test")
    st.markdown("Test the main `/hackrx/run` endpoint with sample data")
    
    # Default sample data
    default_url = "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"
    
    default_questions = [
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?",
        "Does this policy cover maternity expenses, and what are the conditions?",
        "What is the waiting period for cataract surgery?",
        "Are the medical expenses for an organ donor covered under this policy?"
    ]
    
    st.subheader("📋 Request Configuration")
    
    # Document URL input
    document_url = st.text_input(
        "Document URL:",
        value=default_url,
        help="Enter the URL of the document to analyze"
    )
    
    # Questions input
    st.subheader("❓ Questions")
    questions = []
    
    # Pre-populate with default questions
    for i, default_q in enumerate(default_questions):
        question = st.text_area(
            f"Question {i+1}:",
            value=default_q,
            height=60,
            key=f"q_{i}"
        )
        if question.strip():
            questions.append(question.strip())
    
    # Add custom questions
    num_custom = st.number_input("Additional custom questions:", min_value=0, max_value=10, value=0)
    for i in range(num_custom):
        custom_q = st.text_area(
            f"Custom Question {i+1}:",
            height=60,
            key=f"custom_q_{i}"
        )
        if custom_q.strip():
            questions.append(custom_q.strip())
    
    # Submit button
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🚀 Run HackRx API", type="primary"):
            if not document_url:
                st.error("Please enter a document URL")
                return
            
            if not questions:
                st.error("Please enter at least one question")
                return
            
            # Prepare request
            request_data = {
                "documents": document_url,
                "questions": questions
            }
            
            # Show request data
            with st.expander("📤 Request Data"):
                st.json(request_data)
            
            # Make API call
            with st.spinner("Processing document and generating answers..."):
                result = make_api_request("/hackrx/run", request_data, "POST")
            
            if result:
                st.success("✅ Successfully processed!")
                
                # Display results
                st.subheader("📋 Results")
                
                if "answers" in result:
                    for i, (question, answer) in enumerate(zip(questions, result["answers"])):
                        with st.expander(f"Q{i+1}: {question[:100]}..."):
                            st.write("**Question:**")
                            st.write(question)
                            st.write("**Answer:**")
                            st.write(answer)
                
                # Show raw response
                with st.expander("🔍 Raw API Response"):
                    st.json(result)
    
    with col2:
        if st.button("🧹 Clear All"):
            st.experimental_rerun()

def document_upload_page():
    """Document upload and processing page"""
    st.header("📄 Document Upload & Processing")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Upload New Document")
        
        # URL input
        doc_url = st.text_input(
            "Document URL:",
            placeholder="https://example.com/document.pdf",
            help="Enter the URL of the PDF or DOCX document"
        )
        
        # Title input
        doc_title = st.text_input(
            "Document Title (optional):",
            placeholder="Enter a title for the document"
        )
        
        if st.button("📤 Upload & Process Document", type="primary"):
            if not doc_url:
                st.error("Please enter a document URL")
                return
            
            request_data = {
                "url": doc_url,
                "title": doc_title
            }
            
            with st.spinner("Uploading and processing document..."):
                result = make_api_request("/documents/upload", request_data, "POST")
            
            if result:
                st.success(f"✅ {result['message']}")
                st.info(f"Document ID: {result.get('document_id')}")
                st.info(f"Number of chunks: {result.get('chunks')}")
    
    with col2:
        st.subheader("📊 Processing Status")
        if st.button("🔄 Refresh Documents"):
            documents = make_api_request("/documents")
            if documents:
                st.write(f"**Total Documents:** {len(documents)}")
                for doc in documents[-5:]:  # Show last 5
                    st.write(f"- {doc['title'][:30]}...")

def query_documents_page():
    """Query documents page"""
    st.header("🔍 Query Documents")
    
    # Get list of documents
    documents = make_api_request("/documents")
    
    if not documents:
        st.warning("No documents found. Please upload a document first.")
        return
    
    # Document selection
    doc_options = {doc['url']: f"{doc['title']} (ID: {doc['id']})" for doc in documents}
    selected_url = st.selectbox(
        "Select Document:",
        options=list(doc_options.keys()),
        format_func=lambda x: doc_options[x]
    )
    
    # Question input
    question = st.text_area(
        "Enter your question:",
        height=100,
        placeholder="What specific information are you looking for in this document?"
    )
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("🔍 Ask Question", type="primary"):
            if not question.strip():
                st.error("Please enter a question")
                return
            
            request_data = {
                "document_url": selected_url,
                "question": question
            }
            
            with st.spinner("Searching document and generating answer..."):
                result = make_api_request("/query", request_data, "POST")
            
            if result:
                st.subheader("💬 Answer")
                st.write(result["answer"])
                
                if "relevant_chunks" in result and result["relevant_chunks"]:
                    with st.expander("📚 Relevant Document Sections"):
                        for i, chunk in enumerate(result["relevant_chunks"]):
                            st.write(f"**Section {i+1}** (Score: {chunk.get('score', 'N/A'):.3f})")
                            st.write(chunk["text"])
                            st.write("---")

def document_management_page():
    """Document management page"""
    st.header("📚 Document Management")
    
    # Get documents
    documents = make_api_request("/documents")
    
    if not documents:
        st.info("No documents found.")
        return
    
    st.subheader(f"📋 All Documents ({len(documents)})")
    
    for doc in documents:
        with st.expander(f"📄 {doc['title']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**ID:** {doc['id']}")
                st.write(f"**URL:** {doc['url']}")
                st.write(f"**Created:** {doc['created_at']}")
                st.write(f"**Chunks:** {doc.get('chunks', {}).get('count', 'N/A')}")
            
            with col2:
                if st.button(f"📊 View Queries", key=f"queries_{doc['id']}"):
                    queries = make_api_request(f"/documents/{doc['id']}/queries")
                    if queries:
                        st.subheader("Previous Queries")
                        for query in queries[-5:]:  # Show last 5
                            st.write(f"**Q:** {query['question'][:100]}...")
                            st.write(f"**A:** {query['answer'][:200]}...")
                            st.write("---")
                    else:
                        st.info("No queries found for this document.")

if __name__ == "__main__":
    main()
