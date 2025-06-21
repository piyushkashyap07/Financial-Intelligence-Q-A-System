# MAG7 Financial Intelligence Q&A System - Codebase Index

## 🏗️ **System Architecture Overview**

The MAG7 Financial Intelligence Q&A System is a modern AI-powered platform that provides intelligent analysis of the "Magnificent 7" technology companies (AAPL, MSFT, AMZN, GOOGL, META, NVDA, TSLA) using their SEC filings from 2015-2025.

### **Core Technologies:**
- **LlamaIndex Workflow** - Multi-step reasoning and query classification
- **Google Gemini** - LLM and embedding generation
- **Pinecone** - Vector database with integrated embeddings
- **Streamlit** - Web interface
- **FastAPI** - API endpoints (LlamaIndex POC)

---

## 📁 **Directory Structure**

```
unique/
├── app.py                          # Main Streamlit web application
├── cli_app.py                      # Command-line interface
├── conversational_agent.py         # LlamaIndex workflow agent
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (create from env.example)
├── env.example                    # Environment variables template
├── Makefile                       # Build and deployment commands
├── README.md                      # Project documentation
├── CODEBASE_INDEX.md              # This file - comprehensive code index
├── FUNCTION_INDEX.md              # Function reference guide
├── QUICK_REFERENCE.md             # Quick start and troubleshooting
├── TECHNICAL_REPORT.md            # Technical implementation details
├── SECURITY.md                    # Security considerations
├── LLAMAINDEX_INTEGRATION.md      # LlamaIndex workflow details
│
├── data_storing/                  # Data processing modules
│   ├── sec_data.py               # SEC filing data handling
│   └── text_cleaning.py          # Text preprocessing utilities
│
├── storing_vector_db/             # Vector database operations
│   ├── embeddings.py             # Pinecone integration with integrated embeddings
│   ├── retrieval.py              # Vector search and RAG operations
│   └── upload_to_pinecone.py     # Data upload to Pinecone
│
├── processed_filings/             # Processed SEC filing data
│   ├── all_chunks.json           # All processed chunks
│   ├── consolidated_processed_filings.json
│   └── [company]_[filing]_processed.json files
│
├── sec_filings_data/              # Raw SEC filing HTML files
│   ├── AAPL/, MSFT/, AMZN/, etc. # Company-specific filing directories
│   ├── filing_metadata.csv       # Filing metadata
│   └── filing_metadata.json      # Filing metadata in JSON format
│
├── llamaindex-poc/                # LlamaIndex POC implementation
│   ├── app/                      # FastAPI application
│   │   ├── api/v1/               # API endpoints
│   │   ├── core/                 # Configuration
│   │   ├── db/                   # Database connections
│   │   ├── models/               # Data models
│   │   ├── prompts/              # LLM prompts
│   │   ├── schemas/              # Pydantic schemas
│   │   ├── services/             # Business logic
│   │   ├── tools/                # Custom tools
│   │   └── utils/                # Utility functions
│   ├── tests/                    # Test suite
│   ├── requirements.txt          # POC dependencies
│   └── run.py                    # POC runner
│
└── venv/                         # Python virtual environment
```

---

## 🔧 **Core Components**

### **1. Conversational Agent (`conversational_agent.py`)**
**Purpose**: Main LlamaIndex workflow for intelligent query processing

**Key Classes:**
- `MAG7FinancialWorkflow` - LlamaIndex workflow with multi-step reasoning
- `MAG7ConversationalAgent` - High-level agent interface

**Workflow Steps:**
1. `classify_query` - Query classification (FINANCIAL_RAG, COMPARATIVE_ANALYSIS, TREND_ANALYSIS, GENERAL_QUERY)
2. `financial_rag_step` - Financial data retrieval and analysis
3. `comparative_analysis_step` - Cross-company comparisons
4. `trend_analysis_step` - Historical trend analysis
5. `general_query_step` - General questions and greetings

**Features:**
- ✅ Query classification with 95% confidence
- ✅ Multi-step reasoning
- ✅ Context-aware conversations
- ✅ Fallback mode when Pinecone unavailable

### **2. Web Interface (`app.py`)**
**Purpose**: Streamlit web application for user interaction

**Features:**
- Modern UI with custom CSS
- Example queries sidebar
- Conversation history management
- Real-time query processing
- Source citation display
- Metrics dashboard

### **3. CLI Interface (`cli_app.py`)**
**Purpose**: Command-line interface for system interaction

**Features:**
- Interactive chat mode
- Environment variable checking
- Direct query processing
- Conversation management

### **4. Vector Database (`storing_vector_db/`)**
**Purpose**: Modern Pinecone integration with integrated embeddings

**Key Files:**
- `embeddings.py` - Pinecone index creation and data upload
- `retrieval.py` - Vector search and RAG operations
- `upload_to_pinecone.py` - Data upload orchestration

**Modern Features:**
- ✅ Integrated embeddings (no local embedding generation)
- ✅ Raw text upsert (Pinecone handles vectorization)
- ✅ Structured IDs and comprehensive metadata
- ✅ Namespace support for organized data
- ✅ Text-based search queries

---

## 🚀 **Key Features**

### **Intelligent Query Classification**
- **FINANCIAL_RAG**: Specific financial metrics and data
- **COMPARATIVE_ANALYSIS**: Cross-company comparisons
- **TREND_ANALYSIS**: Historical patterns and trends
- **GENERAL_QUERY**: Greetings and general information

### **Multi-Step Reasoning**
- Query understanding and classification
- Context retrieval from vector database
- Specialized processing based on query type
- Response generation with citations

### **Modern Vector Database**
- **Integrated Embeddings**: Pinecone handles vectorization
- **Structured Data**: Organized metadata and IDs
- **Efficient Search**: Text-based queries with filtering
- **Scalable Architecture**: Ready for production use

### **Robust Error Handling**
- Fallback mode when Pinecone unavailable
- Graceful degradation of functionality
- Comprehensive logging and debugging
- User-friendly error messages

---

## 🔑 **Environment Variables**

### **Required Variables:**
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

## 🎯 **Usage Examples**

### **Web Interface**
```bash
streamlit run app.py
```
Access at: http://localhost:8501

### **CLI Interface**
```bash
python cli_app.py
```

### **Upload Data to Pinecone**
```bash
python storing_vector_db/upload_to_pinecone.py
```

### **Test System**
```bash
python -c "from conversational_agent import mag7_agent; import asyncio; result = asyncio.run(mag7_agent.process_message('test', 'What was Microsoft revenue in 2024?')); print(result)"
```

---

## 🔧 **Development Commands**

### **Setup Environment**
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your API keys
```

### **Data Processing**
```bash
# Process SEC filings
python -c "from data_storing.text_cleaning import SECTextProcessor; processor = SECTextProcessor(); processor.process_all_filings()"

# Upload to Pinecone (requires valid API key)
python storing_vector_db/upload_to_pinecone.py
```

### **Testing**
```bash
# Test LlamaIndex workflow
python -c "from conversational_agent import mag7_agent; import asyncio; result = asyncio.run(mag7_agent.process_message('test', 'Hello')); print(result)"

# Test vector retrieval
python -c "from storing_vector_db.retrieval import get_relevant_chunks; import asyncio; result = asyncio.run(get_relevant_chunks('Microsoft revenue')); print(result)"
```

---

## 📊 **Data Flow**

### **1. Data Ingestion**
```
SEC HTML Files → Text Cleaning → Chunking → JSON Storage
```

### **2. Vector Database**
```
JSON Chunks → Pinecone Upload → Integrated Embeddings → Vector Search
```

### **3. Query Processing**
```
User Query → Classification → Context Retrieval → LLM Response → Citations
```

### **4. Response Generation**
```
Query Type → Specialized Processing → Context Integration → Structured Response
```

---

## 🛡️ **Security Considerations**

### **API Key Management**
- Environment variables for sensitive data
- No hardcoded credentials
- Secure key rotation support

### **Data Privacy**
- Local processing of SEC filings
- No external data transmission beyond API calls
- Secure vector database access

### **Access Control**
- No user authentication (development system)
- API key-based service access
- Environment-specific configurations

---

## 🔄 **System States**

### **Full Functionality Mode**
- ✅ Pinecone API key valid
- ✅ Vector database accessible
- ✅ SEC filing data available
- ✅ Complete RAG capabilities

### **Fallback Mode**
- ✅ Google API key valid
- ✅ LlamaIndex workflow functional
- ✅ General knowledge responses
- ⚠️ No SEC filing specific data

### **Error Mode**
- ❌ API keys invalid
- ❌ Services unavailable
- ✅ Basic error handling
- ✅ User-friendly messages

---

## 📈 **Performance Characteristics**

### **Query Processing**
- **Classification**: ~1-2 seconds
- **Context Retrieval**: ~2-3 seconds (with Pinecone)
- **Response Generation**: ~3-5 seconds
- **Total Response Time**: ~6-10 seconds

### **Scalability**
- **Vector Database**: Supports millions of vectors
- **Concurrent Users**: Limited by Streamlit (single-threaded)
- **Memory Usage**: ~2-4 GB for full dataset
- **Storage**: ~1-2 GB for processed data

---

## 🎯 **Future Enhancements**

### **Planned Features**
- User authentication and session management
- Advanced analytics and visualization
- Real-time data updates
- Multi-language support
- Mobile application

### **Technical Improvements**
- Redis caching for performance
- Database integration for user data
- Advanced filtering and search
- Automated data pipeline
- Monitoring and analytics

---

## 📞 **Support and Maintenance**

### **Troubleshooting**
- Check `QUICK_REFERENCE.md` for common issues
- Review `FUNCTION_INDEX.md` for detailed function documentation
- Use debug logging for detailed error analysis

### **Maintenance**
- Regular API key rotation
- Data updates for new SEC filings
- Performance monitoring
- Security updates

---

*Last Updated: June 21, 2025*
*Version: 2.0 - Modern Pinecone Integration* 