# MAG7 Financial Intelligence Q&A System

An AI-powered retrieval-augmented generation (RAG) chatbot designed to answer complex questions about the "Magnificent 7" technology stocks (AAPL, MSFT, AMZN, GOOGL, META, NVDA, TSLA) using their SEC filings from 2015-2025.

## 🚀 Features

- **LlamaIndex Workflow Architecture**: Multi-step reasoning with intelligent query classification and routing
- **Automated SEC Scraper**: Downloads 10-K and 10-Q filings from EDGAR database
- **Advanced Text Processing**: Converts HTML filings into structured chunks with rich metadata
- **Modern Vector Search**: Uses Pinecone with integrated embeddings for efficient retrieval
- **Conversational Agent**: Maintains context and handles complex multi-step queries
- **Multiple Interfaces**: Streamlit web app and CLI interface
- **Production Ready**: Docker support, comprehensive error handling, and monitoring
- **Comprehensive Documentation**: 11 detailed documentation files for easy navigation

## 🏗️ Architecture

### LlamaIndex Workflow System

The system uses LlamaIndex's workflow architecture for intelligent query processing:

```
User Query → Classification → Routing → Specialized Processing → Response
```

#### Workflow Steps:

1. **Query Classification**: Automatically categorizes queries into:
   - `FINANCIAL_RAG`: Specific financial data requests
   - `COMPARATIVE_ANALYSIS`: Cross-company comparisons
   - `TREND_ANALYSIS`: Historical trend analysis
   - `GENERAL_QUERY`: Greetings and general questions

2. **Specialized Processing**: Each category uses optimized prompts and retrieval strategies

3. **Context Management**: Maintains conversation history for follow-up questions

4. **Source Attribution**: Provides precise citations from SEC filings

### Modern Vector Database Integration

The system uses Pinecone's modern integrated embeddings approach:

```
SEC EDGAR → HTML Files → Text Extraction → Chunking → Raw Text → Pinecone (Integrated Embeddings)
```

**Key Advantages**:
- **Integrated Embeddings**: No local embedding generation required
- **Raw Text Upsert**: Pinecone handles vectorization automatically
- **Structured Metadata**: Comprehensive filing information
- **Efficient Search**: Text-based queries with metadata filtering

## 🛠️ Installation

### Prerequisites

- Python 3.11+
- Google API Key (for Gemini)
- Pinecone API Key (optional for full functionality)
- SEC User Agent (for EDGAR access)

### Quick Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd unique
   ```

2. **Install dependencies**:
   ```bash
   make setup
   # or manually:
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

4. **Run the system**:
   ```bash
   # Web interface
   make run
   
   # CLI interface
   make cli
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Required
GOOGLE_API_KEY=your_google_api_key

# Optional (for full functionality)
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
PINECONE_INDEX_NAME=mag7-financial-intelligence-2025

# SEC Configuration
SEC_USER_AGENT=Your Name your@email.com

# Application Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
LOG_LEVEL=INFO
```

### Vector Database Setup

1. **Create Pinecone Index**: The system will automatically create the index if it doesn't exist
2. **Upload Data**: Run the upload script to populate the index with SEC filing data
3. **Fallback Mode**: System works without Pinecone for basic functionality

## 📊 Usage

### Web Interface

Start the Streamlit app:
```bash
make run
# or
streamlit run app.py
```

Features:
- Interactive chat interface
- Example queries sidebar
- Conversation history
- Source citations
- Confidence scores
- System status monitoring
- Metrics dashboard

### CLI Interface

Start the command-line interface:
```bash
make cli
# or
python cli_app.py
```

Commands:
- `ask <question>` - Ask a question about MAG7 companies
- `history` - Show conversation history
- `clear` - Clear conversation history
- `examples` - Show example queries
- `status` - Show system status
- `help` - Show help information

### Example Queries

The system handles various types of financial queries:

**Basic Financial Data**:
- "What was Microsoft's revenue for Q1 2024?"
- "What were Apple's earnings in FY2023?"

**Comparative Analysis**:
- "Compare operating margins for Apple vs Microsoft in 2023"
- "How did inflation affect Amazon vs Google's performance?"

**Trend Analysis**:
- "Which MAG7 company showed the most consistent R&D growth?"
- "What was Tesla's vehicle delivery trend from 2020-2024?"

**Complex Multi-step**:
- "How did COVID-19 impact Amazon's cloud vs retail revenue?"
- "Compare how inflation affected operating margins for Apple vs Microsoft in 2022-2023"

## 🔄 Data Pipeline

### 1. SEC Filing Download

```bash
make scrape
```

Downloads 10-K and 10-Q filings for all MAG7 companies from 2015-2025.

### 2. Text Processing

```bash
make process
```

Converts HTML filings into structured JSON chunks with metadata.

### 3. Vector Database Upload

```bash
make upload
# or
python storing_vector_db/upload_to_pinecone.py
```

Uploads processed chunks to Pinecone using integrated embeddings.

### 4. Full Pipeline

```bash
make pipeline
```

Runs the complete data pipeline from download to vector database.

## 🧪 Testing

### Quick System Test

```bash
make quick-test
```

Tests all system components:
- LlamaIndex workflow agent
- Vector database connection
- Text processing pipeline

### Individual Tests

```bash
make test
```

Runs specific test scripts for SEC downloading and filename parsing.

### Manual Testing

```bash
# Test conversational agent
python -c "from conversational_agent import mag7_agent; import asyncio; result = asyncio.run(mag7_agent.process_message('test', 'Hello')); print(result)"

# Test vector retrieval
python -c "from storing_vector_db.retrieval import get_relevant_chunks; import asyncio; result = asyncio.run(get_relevant_chunks('Microsoft revenue')); print(result)"
```

## 🐳 Docker Deployment

### Build and Run

```bash
# Build image
make build

# Run with Docker Compose
make docker-run

# Stop
make docker-stop
```

### Docker Compose

The system includes a `docker-compose.yml` for easy deployment with all dependencies.

## 📈 Performance

### Response Format

The system returns structured responses:

```json
{
  "answer": "Microsoft reported revenue of $61.9B in Q1 FY2024, representing a 17% year-over-year increase...",
  "sources": [
    {
      "company": "MSFT",
      "filing": "10-Q",
      "period": "Q1 FY2024",
      "snippet": "Total revenue was $61.9 billion, an increase of 17%...",
      "url": "https://www.sec.gov/..."
    }
  ],
  "confidence": 0.95,
  "query_type": "FINANCIAL_RAG"
}
```

### Features

- **Multi-step Reasoning**: Complex queries are broken down and processed step-by-step
- **Context Awareness**: Maintains conversation history for follow-up questions
- **Source Attribution**: Every response includes precise citations
- **Confidence Scoring**: Provides confidence levels for responses
- **Error Handling**: Graceful handling of missing data and edge cases
- **Fallback Mode**: Works without Pinecone for basic functionality

## 🔍 System Components

### Core Modules

- `conversational_agent.py`: LlamaIndex workflow-based conversational agent
- `app.py`: Streamlit web interface
- `cli_app.py`: Command-line interface
- `data_storing/`: SEC data processing pipeline
- `storing_vector_db/`: Vector database operations with integrated embeddings

### LlamaIndex Integration

The system leverages LlamaIndex's workflow capabilities:

- **Workflow Steps**: Modular processing steps for different query types
- **Event System**: Efficient routing between processing stages
- **Context Management**: Shared context across workflow steps
- **Async Processing**: Non-blocking query processing

### Modern Pinecone Integration

- **Integrated Embeddings**: No local embedding generation
- **Raw Text Upsert**: Automatic vectorization by Pinecone
- **Structured Metadata**: Comprehensive filing information
- **Efficient Search**: Text-based queries with filtering

## 🚨 Troubleshooting

### Common Issues

1. **Missing API Keys**: Ensure all required environment variables are set
2. **Vector Database Connection**: Check Pinecone API key and index name
3. **SEC Rate Limiting**: Use proper SEC_USER_AGENT to avoid rate limits
4. **Memory Issues**: Large filings may require increased memory allocation
5. **Pinecone Unauthorized**: Get a new API key if current one is expired

### Debug Mode

Enable debug logging by setting `LOG_LEVEL=DEBUG` in your `.env` file.

### Fallback Mode

The system operates in fallback mode when Pinecone is unavailable:
- ✅ LlamaIndex workflow remains functional
- ✅ General knowledge responses available
- ⚠️ No SEC filing specific data
- ✅ Graceful degradation

## 📚 Documentation

The project includes comprehensive documentation:

### **Core Documentation**
- [CODEBASE_INDEX.md](CODEBASE_INDEX.md) - Complete system architecture overview
- [FUNCTION_INDEX.md](FUNCTION_INDEX.md) - Detailed function reference guide
- [API_REFERENCE.md](API_REFERENCE.md) - Complete API documentation
- [SEARCH_INDEX.md](SEARCH_INDEX.md) - Searchable component index

### **Development Resources**
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - Development workflows and best practices
- [TECHNICAL_REPORT.md](TECHNICAL_REPORT.md) - Technical implementation details
- [LLAMAINDEX_INTEGRATION.md](LLAMAINDEX_INTEGRATION.md) - LlamaIndex workflow details

### **Quick Reference**
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick start and troubleshooting
- [INDEX_SUMMARY.md](INDEX_SUMMARY.md) - Documentation overview and navigation
- [SECURITY.md](SECURITY.md) - Security considerations and best practices

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 🙏 Acknowledgments

- SEC EDGAR database for financial filings
- Google Gemini for AI capabilities
- Pinecone for modern vector database with integrated embeddings
- LlamaIndex for workflow framework
- Streamlit for web interface

---

**Note**: This system is designed for educational and research purposes. Always verify financial data from official sources before making investment decisions. 