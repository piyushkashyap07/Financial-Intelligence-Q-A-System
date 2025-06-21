# MAG7 Financial Intelligence Q&A System - API Reference

## 🔌 **API Reference Guide**

This document provides a comprehensive API reference for the MAG7 Financial Intelligence Q&A System, including all public interfaces, functions, and classes.

---

## 📋 **Table of Contents**

### **🔧 Core APIs**
- [Conversational Agent API](#conversational-agent-api)
- [Vector Database API](#vector-database-api)
- [Data Processing API](#data-processing-api)
- [Web Interface API](#web-interface-api)
- [CLI Interface API](#cli-interface-api)

### **🚀 Integration APIs**
- [LlamaIndex Workflow API](#llamaindex-workflow-api)
- [Pinecone Integration API](#pinecone-integration-api)
- [Google Gemini API](#google-gemini-api)

---

## 🔧 **Core APIs**

### **Conversational Agent API**

#### **Class: `MAG7ConversationalAgent`**

**Purpose**: High-level interface for conversation management

**Location**: `conversational_agent.py`

**Constructor**:
```python
MAG7ConversationalAgent(
    google_api_key: str = None,
    pinecone_api_key: str = None,
    pinecone_index_name: str = "mag7-financial-intelligence-2025"
)
```

**Methods**:

##### `process_message(conversation_id: str, user_message: str) -> dict`
**Purpose**: Process user message and return response

**Parameters**:
- `conversation_id` (str): Unique conversation identifier
- `user_message` (str): User's input message

**Returns**:
```python
{
    "response": str,           # Generated response
    "confidence": float,       # Confidence score (0-1)
    "query_type": str,        # Query classification
    "sources": list,          # Source citations
    "conversation_id": str    # Conversation ID
}
```

**Example**:
```python
from conversational_agent import MAG7ConversationalAgent

agent = MAG7ConversationalAgent()
result = await agent.process_message("conv_123", "What was Microsoft's revenue in 2024?")
print(result["response"])
```

##### `get_conversation_history(conversation_id: str) -> list`
**Purpose**: Retrieve conversation history

**Parameters**:
- `conversation_id` (str): Conversation identifier

**Returns**: List of conversation messages

##### `clear_conversation_history(conversation_id: str) -> bool`
**Purpose**: Clear conversation history

**Parameters**:
- `conversation_id` (str): Conversation identifier

**Returns**: True if successful

---

#### **Class: `MAG7FinancialWorkflow`**

**Purpose**: LlamaIndex workflow for multi-step reasoning

**Location**: `conversational_agent.py`

**Methods**:

##### `classify_query(user_query: str, conversation_context: str = "") -> dict`
**Purpose**: Classify user query into categories

**Parameters**:
- `user_query` (str): User's input query
- `conversation_context` (str): Previous conversation context

**Returns**:
```python
{
    "query_type": str,        # FINANCIAL_RAG, COMPARATIVE_ANALYSIS, TREND_ANALYSIS, GENERAL_QUERY
    "confidence": float,      # Classification confidence (0-1)
    "reasoning": str         # Classification reasoning
}
```

##### `financial_rag_step(user_query: str, conversation_context: str = "") -> dict`
**Purpose**: Process financial data retrieval queries

**Returns**:
```python
{
    "response": str,          # Generated response
    "sources": list,         # Source citations
    "confidence": float      # Response confidence
}
```

##### `comparative_analysis_step(user_query: str, conversation_context: str = "") -> dict`
**Purpose**: Process cross-company comparison queries

##### `trend_analysis_step(user_query: str, conversation_context: str = "") -> dict`
**Purpose**: Process historical trend analysis queries

##### `general_query_step(user_query: str, conversation_context: str = "") -> dict`
**Purpose**: Process general questions and greetings

---

### **Vector Database API**

#### **Module: `storing_vector_db.embeddings`**

**Location**: `storing_vector_db/embeddings.py`

##### `create_pinecone_index(index_name: str, dimension: int = 768) -> pinecone.Index`
**Purpose**: Create Pinecone index with integrated embeddings

**Parameters**:
- `index_name` (str): Name of the index
- `dimension` (int): Vector dimension (default: 768)

**Returns**: Pinecone index object

**Example**:
```python
from storing_vector_db.embeddings import create_pinecone_index

index = create_pinecone_index("mag7-financial-intelligence-2025")
```

##### `load_and_upload_all_chunks(json_path: str, index_name: str, batch_size: int = 100) -> dict`
**Purpose**: Upload SEC filing chunks to Pinecone

**Parameters**:
- `json_path` (str): Path to JSON file with chunks
- `index_name` (str): Pinecone index name
- `batch_size` (int): Upload batch size

**Returns**:
```python
{
    "total_chunks": int,      # Total chunks processed
    "successful_uploads": int, # Successfully uploaded chunks
    "errors": list           # Error messages
}
```

**Example**:
```python
from storing_vector_db.embeddings import load_and_upload_all_chunks

result = load_and_upload_all_chunks(
    "processed_filings/all_chunks.json",
    "mag7-financial-intelligence-2025"
)
print(f"Uploaded {result['successful_uploads']} chunks")
```

---

#### **Module: `storing_vector_db.retrieval`**

**Location**: `storing_vector_db/retrieval.py`

##### `query_pinecone(query: str, index_name: str, top_k: int = 5, filter_dict: dict = None) -> list`
**Purpose**: Query Pinecone using integrated embeddings

**Parameters**:
- `query` (str): Search query text
- `index_name` (str): Pinecone index name
- `top_k` (int): Number of results to return
- `filter_dict` (dict): Metadata filters

**Returns**: List of matching documents with scores

**Example**:
```python
from storing_vector_db.retrieval import query_pinecone

results = query_pinecone(
    "Microsoft revenue 2024",
    "mag7-financial-intelligence-2025",
    top_k=5
)
for result in results:
    print(f"Score: {result.score}, Content: {result.metadata['content'][:100]}...")
```

##### `get_relevant_chunks(query: str, top_k: int = 8, index_name: str = "mag7-financial-intelligence-2025") -> list`
**Purpose**: Get relevant chunks from vector database (async)

**Parameters**:
- `query` (str): Search query
- `top_k` (int): Number of chunks to retrieve
- `index_name` (str): Pinecone index name

**Returns**: List of relevant chunks with metadata

**Example**:
```python
from storing_vector_db.retrieval import get_relevant_chunks
import asyncio

chunks = asyncio.run(get_relevant_chunks("Apple revenue", top_k=5))
for chunk in chunks:
    print(f"Company: {chunk['company']}, Year: {chunk['year']}")
```

##### `rag_answer(user_query: str, index_name: str = "mag7-financial-intelligence-2025", top_k: int = 5, model_name: str = "models/gemini-1.5-flash-latest", chat_history: list = None) -> dict`
**Purpose**: Complete RAG pipeline for answering questions

**Parameters**:
- `user_query` (str): User's question
- `index_name` (str): Pinecone index name
- `top_k` (int): Number of context chunks
- `model_name` (str): LLM model name
- `chat_history` (list): Previous conversation

**Returns**:
```python
{
    "answer": str,            # Generated answer
    "sources": list,         # Source citations
    "confidence": float,     # Answer confidence
    "query_type": str       # Query classification
}
```

**Example**:
```python
from storing_vector_db.retrieval import rag_answer

answer = rag_answer("What was Tesla's revenue in 2024?")
print(f"Answer: {answer['answer']}")
```

##### `build_sec_url(company: str, accession_number: str, source_file: str) -> str`
**Purpose**: Build SEC filing URL from metadata

**Parameters**:
- `company` (str): Company ticker
- `accession_number` (str): SEC accession number
- `source_file` (str): Source file name

**Returns**: Complete SEC filing URL

---

### **Data Processing API**

#### **Class: `SECTextProcessor`**

**Location**: `data_storing/text_cleaning.py`

**Purpose**: Process SEC filing HTML files into structured chunks

**Methods**:

##### `process_all_filings() -> dict`
**Purpose**: Process all SEC filings in the data directory

**Returns**:
```python
{
    "total_files": int,       # Total files processed
    "successful_files": int,  # Successfully processed files
    "errors": list           # Error messages
}
```

**Example**:
```python
from data_storing.text_cleaning import SECTextProcessor

processor = SECTextProcessor()
result = processor.process_all_filings()
print(f"Processed {result['successful_files']} files")
```

##### `process_company_filings(company: str) -> dict`
**Purpose**: Process filings for a specific company

**Parameters**:
- `company` (str): Company ticker (e.g., "AAPL", "MSFT")

**Returns**: Processing result dictionary

##### `clean_text_for_query(text: str) -> str`
**Purpose**: Clean and normalize text for search queries

**Parameters**:
- `text` (str): Raw text to clean

**Returns**: Cleaned text string

---

#### **Function: `clean_text_for_query(text: str) -> str`**

**Location**: `data_storing/text_cleaning.py`

**Purpose**: Standalone text cleaning function

**Parameters**:
- `text` (str): Text to clean

**Returns**: Cleaned text

**Example**:
```python
from data_storing.text_cleaning import clean_text_for_query

cleaned = clean_text_for_query("<p>Microsoft's revenue was $198.3 billion</p>")
print(cleaned)  # "Microsoft's revenue was $198.3 billion"
```

---

### **Web Interface API**

#### **Module: `app`**

**Location**: `app.py`

**Purpose**: Streamlit web application

##### `main()`
**Purpose**: Main Streamlit application entry point

**Usage**:
```bash
streamlit run app.py
```

##### `run_async_query(agent, conversation_id: str, user_query: str) -> dict`
**Purpose**: Handle async query processing with proper event loop management

**Parameters**:
- `agent`: MAG7ConversationalAgent instance
- `conversation_id` (str): Conversation identifier
- `user_query` (str): User's query

**Returns**: Query result dictionary

##### `display_sources(sources: list)`
**Purpose**: Display source citations in formatted way

**Parameters**:
- `sources` (list): List of source dictionaries

##### `format_confidence(confidence: float) -> str`
**Purpose**: Format confidence scores with color coding

**Parameters**:
- `confidence` (float): Confidence score (0-1)

**Returns**: Formatted confidence string

##### `create_metrics_dashboard()`
**Purpose**: Create metrics dashboard for MAG7 companies

**Returns**: Streamlit dashboard components

---

### **CLI Interface API**

#### **Module: `cli_app`**

**Location**: `cli_app.py`

**Purpose**: Command-line interface

##### `main()`
**Purpose**: CLI application entry point

**Usage**:
```bash
python cli_app.py
```

##### `check_environment() -> bool`
**Purpose**: Check environment variable configuration

**Returns**: True if all required variables are set

##### `interactive_chat(agent)`
**Purpose**: Interactive chat loop for CLI

**Parameters**:
- `agent`: MAG7ConversationalAgent instance

---

## 🚀 **Integration APIs**

### **LlamaIndex Workflow API**

#### **Workflow Steps**

The LlamaIndex workflow consists of five main steps:

1. **Query Classification** (`classify_query`)
2. **Financial RAG** (`financial_rag_step`)
3. **Comparative Analysis** (`comparative_analysis_step`)
4. **Trend Analysis** (`trend_analysis_step`)
5. **General Query** (`general_query_step`)

#### **Query Types**

- `FINANCIAL_RAG`: Specific financial metrics and data
- `COMPARATIVE_ANALYSIS`: Cross-company comparisons
- `TREND_ANALYSIS`: Historical patterns and trends
- `GENERAL_QUERY`: Greetings and general information

---

### **Pinecone Integration API**

#### **Modern Features**

- **Integrated Embeddings**: No local embedding generation
- **Raw Text Upsert**: Pinecone handles vectorization
- **Structured Metadata**: Comprehensive filing information
- **Namespace Support**: Organized data storage
- **Text-Based Search**: Natural language queries

#### **Index Configuration**

```python
{
    "name": "mag7-financial-intelligence-2025",
    "dimension": 768,
    "metric": "cosine",
    "cloud": "aws",
    "region": "us-east-1"
}
```

#### **Metadata Structure**

```python
{
    "company": str,           # Company ticker
    "filing_type": str,      # Filing type (10-K, 10-Q, etc.)
    "year": int,            # Filing year
    "quarter": str,         # Quarter (Q1, Q2, Q3, Q4)
    "section": str,         # Filing section
    "content": str,         # Text content
    "source_file": str,     # Source file name
    "accession_number": str # SEC accession number
}
```

---

### **Google Gemini API**

#### **Model Configuration**

```python
{
    "model": "models/gemini-1.5-flash-latest",
    "temperature": 0.1,
    "max_tokens": 2048,
    "top_p": 0.8,
    "top_k": 40
}
```

#### **Embedding Configuration**

```python
{
    "model": "models/embedding-001",
    "dimension": 768
}
```

---

## 🔑 **Environment Variables API**

### **Required Variables**

```bash
# Google AI Configuration
GOOGLE_API_KEY=your_google_api_key_here

# Pinecone Vector Database (Optional)
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
PINECONE_INDEX_NAME=mag7-financial-intelligence-2025

# SEC Scraper Configuration
SEC_USER_AGENT=Student Research your_email@domain.com

# Application Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
LOG_LEVEL=INFO
```

### **Loading Environment Variables**

```python
from dotenv import load_dotenv
import os

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")
```

---

## 🎯 **Usage Examples**

### **Basic Query Processing**

```python
from conversational_agent import MAG7ConversationalAgent
import asyncio

# Initialize agent
agent = MAG7ConversationalAgent()

# Process query
result = asyncio.run(agent.process_message(
    conversation_id="test_conv",
    user_message="What was Microsoft's revenue in 2024?"
))

print(f"Response: {result['response']}")
print(f"Confidence: {result['confidence']}")
print(f"Query Type: {result['query_type']}")
```

### **Vector Database Operations**

```python
from storing_vector_db.retrieval import get_relevant_chunks, rag_answer
import asyncio

# Get relevant chunks
chunks = asyncio.run(get_relevant_chunks("Apple revenue", top_k=5))
for chunk in chunks:
    print(f"Company: {chunk['company']}, Year: {chunk['year']}")

# Complete RAG response
answer = rag_answer("Compare Apple vs Microsoft revenue")
print(f"Answer: {answer['answer']}")
```

### **Data Processing**

```python
from data_storing.text_cleaning import SECTextProcessor

# Process SEC filings
processor = SECTextProcessor()
result = processor.process_all_filings()
print(f"Processed {result['successful_files']} files")
```

### **Web Interface**

```python
import streamlit as st
from conversational_agent import MAG7ConversationalAgent

# Initialize agent
agent = MAG7ConversationalAgent()

# Streamlit interface
st.title("MAG7 Financial Intelligence")
user_query = st.text_input("Ask a question about MAG7 companies:")
if user_query:
    result = asyncio.run(agent.process_message("web_conv", user_query))
    st.write(result["response"])
```

---

## 🔍 **Error Handling**

### **Common Error Types**

1. **API Key Errors**: Invalid or missing API keys
2. **Connection Errors**: Network or service issues
3. **Index Errors**: Pinecone index not found
4. **JSON Errors**: LLM response parsing issues

### **Error Response Format**

```python
{
    "error": str,            # Error message
    "error_type": str,       # Error category
    "fallback_mode": bool,   # Whether fallback mode is active
    "suggestion": str        # Suggested action
}
```

### **Fallback Mode**

When Pinecone is unavailable, the system operates in fallback mode:
- ✅ LlamaIndex workflow remains functional
- ✅ General knowledge responses available
- ⚠️ No SEC filing specific data
- ✅ Graceful degradation

---

*Last Updated: June 21, 2025*
*Version: 2.0 - Modern Pinecone Integration* 