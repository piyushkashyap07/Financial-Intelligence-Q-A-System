# MAG7 Financial Intelligence Q&A System - Search Index

## 🔍 **Quick Search Reference**

This document provides a searchable index of all major components, functions, and features in the MAG7 Financial Intelligence Q&A System.

---

## 📋 **Search Categories**

### **🔧 Core Components**
- [Conversational Agent](#conversational-agent)
- [Web Interface](#web-interface)
- [CLI Interface](#cli-interface)
- [Vector Database](#vector-database)
- [Data Processing](#data-processing)

### **🚀 Key Features**
- [Query Classification](#query-classification)
- [Multi-step Reasoning](#multi-step-reasoning)
- [Integrated Embeddings](#integrated-embeddings)
- [RAG Pipeline](#rag-pipeline)
- [Error Handling](#error-handling)

### **📁 Files and Functions**
- [Main Files](#main-files)
- [Vector Database Files](#vector-database-files)
- [Data Processing Files](#data-processing-files)
- [Configuration Files](#configuration-files)

---

## 🔧 **Core Components**

### **Conversational Agent**
**File**: `conversational_agent.py`
**Purpose**: Main LlamaIndex workflow for intelligent query processing

**Key Classes**:
- `MAG7FinancialWorkflow` - Multi-step reasoning workflow
- `MAG7ConversationalAgent` - High-level agent interface

**Workflow Steps**:
1. `classify_query` - Query classification (95% confidence)
2. `financial_rag_step` - Financial data retrieval
3. `comparative_analysis_step` - Cross-company analysis
4. `trend_analysis_step` - Historical trend analysis
5. `general_query_step` - General questions

**Search Terms**: workflow, classification, reasoning, agent, conversation

### **Web Interface**
**File**: `app.py`
**Purpose**: Streamlit web application for user interaction

**Features**:
- Modern UI with custom CSS
- Example queries sidebar
- Conversation history management
- Real-time query processing
- Source citation display

**Search Terms**: streamlit, web, UI, interface, dashboard

### **CLI Interface**
**File**: `cli_app.py`
**Purpose**: Command-line interface for system interaction

**Features**:
- Interactive chat mode
- Environment variable checking
- Direct query processing
- Conversation management

**Search Terms**: CLI, command line, terminal, interactive

### **Vector Database**
**Directory**: `storing_vector_db/`
**Purpose**: Modern Pinecone integration with integrated embeddings

**Files**:
- `embeddings.py` - Index creation and data upload
- `retrieval.py` - Vector search and RAG operations
- `upload_to_pinecone.py` - Data upload orchestration

**Search Terms**: pinecone, vector, embedding, search, retrieval

### **Data Processing**
**Directory**: `data_storing/`
**Purpose**: SEC filing data processing and text cleaning

**Files**:
- `text_cleaning.py` - Text preprocessing utilities
- `sec_data.py` - SEC filing data handling

**Search Terms**: processing, cleaning, SEC, filing, text

---

## 🚀 **Key Features**

### **Query Classification**
**Location**: `conversational_agent.py` - `classify_query` method
**Purpose**: Classify user queries into categories

**Categories**:
- `FINANCIAL_RAG` - Specific financial metrics
- `COMPARATIVE_ANALYSIS` - Cross-company comparisons
- `TREND_ANALYSIS` - Historical patterns
- `GENERAL_QUERY` - Greetings and general info

**Search Terms**: classification, categories, FINANCIAL_RAG, COMPARATIVE_ANALYSIS, TREND_ANALYSIS, GENERAL_QUERY

### **Multi-step Reasoning**
**Location**: `conversational_agent.py` - `MAG7FinancialWorkflow`
**Purpose**: LlamaIndex workflow for complex reasoning

**Steps**:
1. Query classification
2. Context retrieval
3. Specialized processing
4. Response generation

**Search Terms**: workflow, reasoning, multi-step, LlamaIndex

### **Integrated Embeddings**
**Location**: `storing_vector_db/embeddings.py`
**Purpose**: Modern Pinecone integration without local embedding generation

**Features**:
- Raw text upsert
- Automatic vectorization
- Structured metadata
- Namespace support

**Search Terms**: integrated, embeddings, raw text, upsert, vectorization

### **RAG Pipeline**
**Location**: `storing_vector_db/retrieval.py` - `rag_answer` function
**Purpose**: Complete retrieval-augmented generation pipeline

**Components**:
- Context retrieval
- Citation building
- Response generation
- Source attribution

**Search Terms**: RAG, retrieval, augmented, generation, pipeline

### **Error Handling**
**Location**: Throughout codebase
**Purpose**: Robust error handling and fallback mechanisms

**Features**:
- Fallback mode without Pinecone
- Graceful degradation
- User-friendly messages
- Comprehensive logging

**Search Terms**: error, handling, fallback, degradation, logging

---

## 📁 **Files and Functions**

### **Main Files**

#### `app.py`
**Purpose**: Streamlit web application
**Key Functions**:
- `main()` - Application entry point
- `run_async_query()` - Async query processing
- `display_sources()` - Source citation display
- `format_confidence()` - Confidence formatting
- `create_metrics_dashboard()` - Metrics dashboard

**Search Terms**: streamlit, web, async, sources, confidence, metrics

#### `cli_app.py`
**Purpose**: Command-line interface
**Key Functions**:
- `main()` - CLI entry point
- `check_environment()` - Environment checking
- `interactive_chat()` - Interactive chat loop

**Search Terms**: CLI, command line, interactive, chat, environment

#### `conversational_agent.py`
**Purpose**: LlamaIndex workflow agent
**Key Classes**:
- `MAG7FinancialWorkflow` - Main workflow
- `MAG7ConversationalAgent` - Agent interface

**Search Terms**: workflow, agent, conversation, LlamaIndex

### **Vector Database Files**

#### `storing_vector_db/embeddings.py`
**Purpose**: Pinecone integration with integrated embeddings
**Key Functions**:
- `create_pinecone_index()` - Index creation
- `load_and_upload_all_chunks()` - Data upload
- `generate_embeddings()` - Legacy embedding generation

**Search Terms**: pinecone, index, upload, chunks, embeddings

#### `storing_vector_db/retrieval.py`
**Purpose**: Vector search and RAG operations
**Key Functions**:
- `query_pinecone()` - Pinecone queries
- `get_relevant_chunks()` - Chunk retrieval
- `rag_answer()` - Complete RAG pipeline
- `build_sec_url()` - URL building

**Search Terms**: retrieval, search, RAG, chunks, URL

#### `storing_vector_db/upload_to_pinecone.py`
**Purpose**: Data upload orchestration
**Key Functions**:
- `check_environment_variables()` - Environment checking
- `mask_key()` - Key masking for display

**Search Terms**: upload, environment, variables, masking

### **Data Processing Files**

#### `data_storing/text_cleaning.py`
**Purpose**: Text preprocessing utilities
**Key Classes**:
- `SECTextProcessor` - SEC filing processor

**Key Functions**:
- `process_all_filings()` - Process all filings
- `clean_text_for_query()` - Text cleaning

**Search Terms**: cleaning, processing, SEC, text, filings

#### `data_storing/sec_data.py`
**Purpose**: SEC filing data handling
**Key Classes**:
- `SECDataProcessor` - SEC data processor

**Search Terms**: SEC, data, processor, filings

### **Configuration Files**

#### `requirements.txt`
**Purpose**: Python dependencies
**Key Packages**:
- llama-index-core
- llama-index-embeddings-gemini
- llama-index-llms-gemini
- llama-index-workflow
- streamlit
- pinecone
- google-generativeai

**Search Terms**: requirements, dependencies, packages

#### `env.example`
**Purpose**: Environment variables template
**Key Variables**:
- GOOGLE_API_KEY
- PINECONE_API_KEY
- PINECONE_INDEX_NAME
- SEC_USER_AGENT

**Search Terms**: environment, variables, API, keys

#### `Makefile`
**Purpose**: Build and deployment commands
**Key Commands**:
- `make run` - Run web interface
- `make cli` - Run CLI interface
- `make test` - Run tests
- `make clean` - Clean environment

**Search Terms**: make, commands, build, deployment

---

## 🎯 **Common Search Patterns**

### **Setup and Installation**
**Search Terms**: setup, install, environment, configuration
**Files**: `README.md`, `env.example`, `requirements.txt`, `Makefile`

### **API Keys and Authentication**
**Search Terms**: API, keys, authentication, pinecone, google
**Files**: `env.example`, `conversational_agent.py`, `storing_vector_db/`

### **Query Processing**
**Search Terms**: query, processing, classification, workflow
**Files**: `conversational_agent.py`, `app.py`, `cli_app.py`

### **Vector Database**
**Search Terms**: vector, database, pinecone, embeddings, search
**Files**: `storing_vector_db/`, `conversational_agent.py`

### **Data Processing**
**Search Terms**: data, processing, SEC, filings, cleaning
**Files**: `data_storing/`, `processed_filings/`

### **Error Handling**
**Search Terms**: error, handling, fallback, logging
**Files**: Throughout codebase

### **Testing**
**Search Terms**: test, testing, validation, check
**Files**: `test_*.py`, `Makefile`

---

## 🔍 **Quick Search Commands**

### **Find Functions by Name**
```bash
grep -r "def function_name" .
```

### **Find Classes by Name**
```bash
grep -r "class ClassName" .
```

### **Find API Key Usage**
```bash
grep -r "API_KEY" .
```

### **Find Error Handling**
```bash
grep -r "except\|try\|error" .
```

### **Find Configuration**
```bash
grep -r "config\|settings\|env" .
```

---

## 📊 **Component Relationships**

### **Data Flow**
```
SEC HTML Files → Text Cleaning → Chunking → JSON Storage
JSON Storage → Pinecone Upload → Integrated Embeddings → Vector Search
User Query → Classification → Context Retrieval → LLM Response → Citations
```

### **File Dependencies**
```
app.py → conversational_agent.py → storing_vector_db/retrieval.py
cli_app.py → conversational_agent.py → storing_vector_db/retrieval.py
conversational_agent.py → storing_vector_db/retrieval.py → data_storing/text_cleaning.py
storing_vector_db/upload_to_pinecone.py → storing_vector_db/embeddings.py
```

### **Configuration Dependencies**
```
.env → All modules (via load_dotenv)
requirements.txt → Virtual environment
Makefile → All commands
env.example → .env template
```

---

*Last Updated: June 21, 2025*
*Version: 2.0 - Modern Pinecone Integration* 