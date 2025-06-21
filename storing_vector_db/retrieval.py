import os
import sys
# Add project root to sys.path for direct script execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pinecone import Pinecone
from dotenv import load_dotenv
from storing_vector_db.embeddings import generate_embeddings
import logging
import google.generativeai as genai
import json

# Configure logger
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Explicitly set environment variables to ensure they're loaded
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "")
os.environ["PINECONE_API_KEY"] = os.getenv("PINECONE_API_KEY", "")
os.environ["PINECONE_INDEX_NAME"] = os.getenv("PINECONE_INDEX_NAME", "mag7-financial-intelligence-2025")

# Debug: Print API key status for retrieval module
print("🔍 Retrieval Module - API Key Debug:")
pinecone_key = os.environ["PINECONE_API_KEY"]
google_key = os.environ["GOOGLE_API_KEY"]
print(f"PINECONE_API_KEY: {'✅ Set' if pinecone_key else '❌ Not set'}")
print(f"GOOGLE_API_KEY: {'✅ Set' if google_key else '❌ Not set'}")

if pinecone_key:
    print(f"PINECONE_API_KEY (first 10 chars): {pinecone_key[:10]}...")
if google_key:
    print(f"GOOGLE_API_KEY (first 10 chars): {google_key[:10]}...")

# Check if .env file exists from this location
env_file_path = os.path.join(os.path.dirname(__file__), '..', '.env')
print(f".env file exists: {'✅ Yes' if os.path.exists(env_file_path) else '❌ No'}")
print(f".env file path: {env_file_path}")
print("=" * 50)

def build_sec_url(company, accession_number, source_file):
    # This is a placeholder. For real SEC URLs, you need the CIK and accession number without dashes.
    # Example: https://www.sec.gov/Archives/edgar/data/{CIK}/{accession_number_no_dashes}/{filename}
    # If you have CIK mapping, use it. Otherwise, use accession_number and file as best effort.
    if accession_number and source_file:
        acc_no = accession_number.replace('-', '')
        return f"https://www.sec.gov/Archives/edgar/data/{company}/{acc_no}/{source_file}"
    return ""

def query_pinecone(query: str, index_name: str, top_k: int = 5, filter_dict: dict = None):
    """
    Query Pinecone with a natural language query using integrated embeddings.

    Args:
        query: User's question.
        index_name: Name of the Pinecone index.
        top_k: Number of results to return.
        filter_dict: Optional Pinecone metadata filter.

    Returns:
        List of dicts with chunk text, metadata, and similarity score.
    """
    # Connect to Pinecone index
    pc_client = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    index = pc_client.Index(index_name)

    # Query Pinecone using integrated embeddings (search with raw text)
    response = index.search(
        namespace="mag7-financial-data",
        query={
            "inputs": {"text": query},
            "top_k": top_k,
            "filter": filter_dict
        },
        fields=["chunk_text"]
    )

    # Format results
    results = []
    for match in response['matches']:
        metadata = match['metadata']
        results.append({
            "score": match['score'],
            "chunk_id": match['id'],
            "text": metadata.get("chunk_text", ""),
            "company": metadata.get("company"),
            "form_type": metadata.get("form_type"),
            "filing_date": metadata.get("filing_date"),
            "report_date": metadata.get("report_date"),
            "section": metadata.get("section"),
            "subsection": metadata.get("subsection"),
            "chunk_index": metadata.get("chunk_number"),
            "source_file": metadata.get("source_file"),
            "accession_number": metadata.get("accession_number"),
        })
    return results

async def get_relevant_chunks(query: str, top_k: int = 8, index_name: str = "mag7-financial-intelligence-2025"):
    """
    Get relevant chunks from the vector database for a given query.
    This is a wrapper function that provides the interface expected by the conversational agent.
    
    Args:
        query: The search query
        top_k: Number of chunks to retrieve
        index_name: Name of the Pinecone index
        
    Returns:
        List of dictionaries containing chunk information
    """
    try:
        # Use the existing query_pinecone function
        results = query_pinecone(query, index_name, top_k=top_k)
        
        # Transform results to match the expected format
        chunks = []
        for result in results:
            chunk = {
                'company': result.get('company', 'Unknown'),
                'filing_type': result.get('form_type', 'Unknown'),
                'period': result.get('filing_date', 'Unknown'),
                'content': result.get('text', ''),
                'url': build_sec_url(
                    result.get('company'), 
                    result.get('accession_number'), 
                    result.get('source_file')
                ),
                'score': result.get('score', 0.0),
                'section': result.get('section', ''),
                'subsection': result.get('subsection', '')
            }
            chunks.append(chunk)
        
        return chunks
    except Exception as e:
        logger.error(f"Error retrieving chunks: {e}")
        return []

# --- BM25 Hybrid Search (Stub) ---
def bm25_search(query: str, corpus: list, top_k: int = 5):
    """
    Placeholder for BM25 search. Implement with a library like rank_bm25 or ElasticSearch.
    Args:
        query: User's question.
        corpus: List of dicts (chunks) to search over.
        top_k: Number of results to return.
    Returns:
        List of dicts (same format as vector search)
    """
    # TODO: Implement BM25 search
    return []

# --- Cross-Encoder Reranking (Stub) ---
def cross_encoder_rerank(query: str, candidates: list, model_name: str = None, top_k: int = 5):
    """
    Placeholder for cross-encoder reranking. Use a model like sentence-transformers/ms-marco or Gemini Pro.
    Args:
        query: User's question.
        candidates: List of dicts (from vector/BM25 search)
        model_name: Optional model name for reranking
        top_k: Number of reranked results to return
    Returns:
        List of dicts, reranked by relevance
    """
    # TODO: Implement cross-encoder reranking
    return candidates[:top_k]

def rag_answer(user_query, index_name="mag7-financial-intelligence-2025", top_k=5, model_name="models/gemini-1.5-flash-latest", chat_history=None):
    # 1. Retrieve using integrated embeddings
    results = query_pinecone(user_query, index_name, top_k=top_k)
    
    # 2. Build context and citations
    context = ""
    citations = []
    for i, r in enumerate(results):
        context += f"[{i+1}] {r['text']}\n"
        citations.append({
            "company": r["company"],
            "filing": r["form_type"],
            "period": r["filing_date"],
            "snippet": r["text"][:120] + ("..." if len(r["text"]) > 120 else ""),
            "url": build_sec_url(r["company"], r.get("accession_number"), r.get("source_file"))
        })
    
    # 3. Compose prompt with chat history
    prompt = ""
    if chat_history:
        for turn in chat_history:
            prompt += f"{turn['role'].capitalize()}: {turn['content']}\n"
    prompt += (
        f"User: {user_query}\n"
        f"Context:\n{context}\n"
        "Please answer the question using only the provided context. "
        "Return your answer in the following JSON format:\n"
        "{\n"
        '  "answer": "...",\n'
        '  "sources": [ { "company": "...", "filing": "...", "period": "...", "snippet": "...", "url": "..." }, ... ],\n'
        '  "confidence": 0.95\n'
        "}\n"
    )
    
    # 4. Call Gemini
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    
    # 5. Parse and return JSON
    try:
        start = response.text.find('{')
        end = response.text.rfind('}') + 1
        json_str = response.text[start:end]
        return json.loads(json_str)
    except Exception as e:
        logger.error(f"Failed to parse JSON from LLM response: {e}\nRaw response: {response.text}")
        return {"error": "Failed to parse LLM response", "raw": response.text}

if __name__ == "__main__":
    query1 = "What was Microsoft's revenue for Q1 2024?"
    answer1 = rag_answer(query1)
    print("First turn:")
    print(json.dumps(answer1, indent=2))
    print()
    # Simulate a follow-up question using chat history
    chat_history = [
        {"role": "user", "content": query1},
        {"role": "assistant", "content": answer1["answer"] if isinstance(answer1, dict) and "answer" in answer1 else str(answer1)}
    ]
    query2 = "How did that compare to Q1 2023?"
    answer2 = rag_answer(query2, chat_history=chat_history)
    print("Second turn (follow-up):")
    print(json.dumps(answer2, indent=2))

    # Example: Vector search only
    query = "What was Microsoft's revenue for Q1 2024?"
    index_name = "mag7-financial-intelligence-2025"
    results = query_pinecone(query, index_name, top_k=5)
    for r in results:
        print(f"{r['company']} {r['form_type']} {r['filing_date']} | Score: {r['score']}")
        print(r['text'][:300], "...\n")

    # Example: Hybrid search (BM25 + vector) and rerank (stubs)
    # corpus = ... # Load all chunks as a list of dicts
    # bm25_results = bm25_search(query, corpus, top_k=10)
    # vector_results = query_pinecone(query, index_name, top_k=10)
    # combined_candidates = bm25_results + vector_results
    # reranked = cross_encoder_rerank(query, combined_candidates, top_k=5)
    # for r in reranked:
    #     print(r) 