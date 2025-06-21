# MAG7 Financial Intelligence Q&A System - Function Index

## 🔧 **Core Functions Reference**

This document provides a comprehensive reference for all functions in the MAG7 Financial Intelligence Q&A System, updated for modern Pinecone integration with integrated embeddings.

---

## 📁 **Conversational Agent (`conversational_agent.py`)**

### **Main Classes**

#### `MAG7FinancialWorkflow`
**Purpose**: LlamaIndex workflow for multi-step reasoning and query processing

**Key Methods:**
- `classify_query()` - Query classification with 95% confidence
- `financial_rag_step()` - Financial data retrieval and analysis
- `comparative_analysis_step()` - Cross-company comparisons
- `trend_analysis_step()` - Historical trend analysis
- `general_query_step()` - General questions and greetings

**Helper Methods:**
- `_format_conversation_context()` - Format conversation history
- `_extract_json_from_llm_response()` - Parse LLM JSON responses
- `_get_financial_context()` - Retrieve context from vector database

#### `MAG7ConversationalAgent`
**Purpose**: High-level interface for conversation management

**Key Methods:**
- `process_message()` - Main message processing pipeline
- `get_conversation_history()` - Retrieve conversation history
- `clear_conversation_history()` - Clear conversation data

---

## 🗄️ **Vector Database (`storing_vector_db/`)**

### **Embeddings (`embeddings.py`)**

#### `create_pinecone_index(index_name: str, dimension: int = 768)`
**Purpose**: Create Pinecone index with integrated embeddings

**Features:**
- ✅ Modern integrated embedding approach
- ✅ Automatic vector generation from raw text
- ✅ Structured metadata support
- ✅ Namespace organization

**Usage:**
```python
from storing_vector_db.embeddings import create_pinecone_index
index = create_pinecone_index("mag7-financial-intelligence-2025")
```

#### `load_and_upload_all_chunks(json_path: str, index_name: str, batch_size: int = 100)`
**Purpose**: Upload SEC filing chunks to Pinecone using integrated embeddings

**Modern Features:**
- ✅ Raw text upsert (no local embedding generation)
- ✅ Structured IDs: `chunk_id` format
- ✅ Comprehensive metadata
- ✅ Automatic vectorization by Pinecone

**Usage:**
```python
result = load_and_upload_all_chunks("processed_filings/all_chunks.json", "mag7-financial-intelligence-2025")
```

#### `generate_embeddings(text: str) -> List[float]`
**Purpose**: Generate embeddings using Gemini (legacy function, not used with integrated embeddings)

---

### **Retrieval (`retrieval.py`)**

#### `query_pinecone(query: str, index_name: str, top_k: int = 5, filter_dict: dict = None)`
**Purpose**: Query Pinecone using integrated embeddings

**Modern Features:**
- ✅ Text-based search queries
- ✅ Integrated embedding conversion
- ✅ Metadata filtering
- ✅ Namespace support

**Usage:**
```python
results = query_pinecone("What was Microsoft's revenue?", "mag7-financial-intelligence-2025", top_k=5)
```

#### `get_relevant_chunks(query: str, top_k: int = 8, index_name: str = "mag7-financial-intelligence-2025")`
**Purpose**: Get relevant chunks from vector database (async wrapper)

**Usage:**
```python
chunks = await get_relevant_chunks("Microsoft revenue 2024", top_k=8)
```

#### `rag_answer(user_query, index_name="mag7-financial-intelligence-2025", top_k=5, model_name="models/gemini-1.5-flash-latest", chat_history=None)`
**Purpose**: Complete RAG pipeline for answering questions using SEC filings

**Features:**
- ✅ Integrated embedding search
- ✅ Context building with citations
- ✅ Chat history support
- ✅ JSON response format

**Usage:**
```python
answer = rag_answer("What was Apple's revenue in 2024?")
print(answer["answer"])
print(answer["sources"])
```

#### `build_sec_url(company, accession_number, source_file)`
**Purpose**: Build SEC filing URLs from metadata

---

## 🧹 **Data Processing (`data_storing/`)**

### **Text Cleaning (`text_cleaning.py`)**

#### `SECTextProcessor`
**Purpose**: Process SEC filing HTML files into structured chunks

**Key Methods:**
- `process_all_filings()` - Process all SEC filings
- `process_company_filings(company)` - Process specific company
- `clean_text_for_query(text)` - Clean text for search queries

**Usage:**
```python
from data_storing.text_cleaning import SECTextProcessor
processor = SECTextProcessor()
processor.process_all_filings()
```

#### `clean_text_for_query(text: str) -> str`
**Purpose**: Clean and normalize text for search queries

**Features:**
- ✅ Remove HTML tags
- ✅ Normalize whitespace
- ✅ Remove special characters
- ✅ Text standardization

---

### **SEC Data (`sec_data.py`)**

#### `SECDataProcessor`
**Purpose**: Handle SEC filing data operations

**Key Methods:**
- `download_filings()` - Download SEC filings
- `extract_metadata()` - Extract filing metadata
- `process_filings()` - Process filing data

---

## 🌐 **Web Interface (`app.py`)**

### **Main Functions**

#### `main()`
**Purpose**: Main Streamlit application entry point

**Features:**
- ✅ Modern UI with custom CSS
- ✅ Example queries sidebar
- ✅ Conversation history management
- ✅ Real-time query processing
- ✅ Source citation display

#### `run_async_query(agent, conversation_id, user_query)`
**Purpose**: Handle async query processing with proper event loop management

#### `display_sources(sources)`
**Purpose**: Display source citations in formatted way

#### `format_confidence(confidence)`
**Purpose**: Format confidence scores with color coding

#### `create_metrics_dashboard()`
**Purpose**: Create metrics dashboard for MAG7 companies

---

## 💻 **CLI Interface (`cli_app.py`)**

### **Main Functions**

#### `main()`
**Purpose**: Command-line interface entry point

**Features:**
- ✅ Interactive chat mode
- ✅ Environment variable checking
- ✅ Direct query processing
- ✅ Conversation management

#### `check_environment()`
**Purpose**: Check environment variable configuration

#### `interactive_chat(agent)`
**Purpose**: Interactive chat loop for CLI

---

## 🔧 **Utility Functions**

### **Environment Management**

#### `load_dotenv()`
**Purpose**: Load environment variables from .env file

**Usage:**
```python
from dotenv import load_dotenv
load_dotenv()
```

### **Logging**

#### `logging.getLogger(__name__)`
**Purpose**: Configure logging for modules

**Usage:**
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Processing started")
```

---

## 🎯 **Modern Pinecone Integration Features**

### **Integrated Embeddings**
- ✅ **No Local Embedding Generation**: Pinecone handles vectorization
- ✅ **Raw Text Upsert**: Send text, get vectors automatically
- ✅ **Better Performance**: Optimized for Pinecone infrastructure
- ✅ **Simplified Code**: Less complexity and maintenance

### **Structured Data**
- ✅ **Structured IDs**: `chunk_id` format for organization
- ✅ **Comprehensive Metadata**: All SEC filing information
- ✅ **Namespace Support**: Organized data storage
- ✅ **Efficient Filtering**: Query-time metadata filtering

### **Modern Search**
- ✅ **Text-Based Queries**: Natural language search
- ✅ **Integrated Conversion**: Automatic text-to-vector
- ✅ **Advanced Filtering**: Complex metadata filters
- ✅ **Scalable Architecture**: Production-ready

---

## 🔑 **Environment Variables Reference**

### **Required Variables**
```bash
# Google AI Configuration
GOOGLE_API_KEY=your_google_api_key_here

# Pinecone Vector Database (Optional for full functionality)
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

---

## 🚀 **Usage Examples**

### **Basic Query Processing**
```python
from conversational_agent import mag7_agent
import asyncio

# Process a query
result = asyncio.run(mag7_agent.process_message(
    conversation_id="test_conv",
    user_message="What was Microsoft's revenue in 2024?"
))
print(result["response"])
```

### **Vector Database Operations**
```python
from storing_vector_db.retrieval import get_relevant_chunks
import asyncio

# Get relevant chunks
chunks = asyncio.run(get_relevant_chunks("Apple revenue", top_k=5))
for chunk in chunks:
    print(f"Company: {chunk['company']}, Content: {chunk['content'][:100]}...")
```

### **RAG Pipeline**
```python
from storing_vector_db.retrieval import rag_answer

# Complete RAG response
answer = rag_answer("Compare Apple vs Microsoft revenue")
print(f"Answer: {answer['answer']}")
print(f"Sources: {len(answer['sources'])} sources found")
```

### **Data Processing**
```python
from data_storing.text_cleaning import SECTextProcessor

# Process SEC filings
processor = SECTextProcessor()
processor.process_all_filings()
```

---

## 🔍 **Error Handling**

### **Common Error Patterns**
- **401 Unauthorized**: Invalid API keys
- **Index Not Found**: Pinecone index doesn't exist
- **Connection Errors**: Network or service issues
- **JSON Parsing Errors**: LLM response format issues

### **Fallback Mechanisms**
- ✅ **Graceful Degradation**: System works without Pinecone
- ✅ **Error Recovery**: Automatic retry and fallback
- ✅ **User-Friendly Messages**: Clear error communication
- ✅ **Logging**: Comprehensive error tracking

---

*Last Updated: June 21, 2025*
*Version: 2.0 - Modern Pinecone Integration* 