# MAG7 Financial Intelligence Q&A System - Development Guide

## 🛠️ **Development Guide**

This document provides comprehensive guidance for developers working on the MAG7 Financial Intelligence Q&A System, including setup, development workflows, testing, and deployment.

---

## 📋 **Table of Contents**

### **🚀 Getting Started**
- [Environment Setup](#environment-setup)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [Configuration](#configuration)

### **🔧 Development Workflows**
- [Local Development](#local-development)
- [Testing](#testing)
- [Debugging](#debugging)
- [Code Quality](#code-quality)

### **📦 Deployment**
- [Docker Deployment](#docker-deployment)
- [Production Setup](#production-setup)
- [Monitoring](#monitoring)

### **🔍 Troubleshooting**
- [Common Issues](#common-issues)
- [Performance Optimization](#performance-optimization)
- [Security Considerations](#security-considerations)

---

## 🚀 **Getting Started**

### **Environment Setup**

#### **Prerequisites**
- Python 3.9+
- Git
- Docker (optional)
- API Keys (Google AI, Pinecone)

#### **Quick Start**
```bash
# Clone the repository
git clone <repository-url>
cd unique

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your API keys

# Test the system
python -c "from conversational_agent import mag7_agent; import asyncio; result = asyncio.run(mag7_agent.process_message('test', 'Hello')); print(result)"
```

#### **Required API Keys**
1. **Google AI API Key**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Add to `.env`: `GOOGLE_API_KEY=your_key_here`

2. **Pinecone API Key** (Optional for full functionality)
   - Visit [Pinecone Console](https://app.pinecone.io/)
   - Create a new API key
   - Add to `.env`: `PINECONE_API_KEY=your_key_here`

3. **SEC User Agent**
   - Add to `.env`: `SEC_USER_AGENT=Student Research your_email@domain.com`

---

### **Project Structure**

```
unique/
├── app.py                          # Main Streamlit web application
├── cli_app.py                      # Command-line interface
├── conversational_agent.py         # LlamaIndex workflow agent
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables
├── env.example                    # Environment variables template
├── Makefile                       # Build and deployment commands
├── README.md                      # Project documentation
├── CODEBASE_INDEX.md              # Comprehensive code index
├── FUNCTION_INDEX.md              # Function reference guide
├── SEARCH_INDEX.md                # Searchable index
├── API_REFERENCE.md               # API documentation
├── DEVELOPMENT_GUIDE.md           # This file
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
├── sec_filings_data/              # Raw SEC filing HTML files
├── llamaindex-poc/                # LlamaIndex POC implementation
└── venv/                         # Python virtual environment
```

---

### **Dependencies**

#### **Core Dependencies**
```txt
# LlamaIndex Workflow
llama-index-core>=0.10.0
llama-index-embeddings-gemini>=0.1.0
llama-index-llms-gemini>=0.1.0
llama-index-workflow>=0.1.0

# Vector Database
pinecone-client>=3.0.0

# Web Framework
streamlit>=1.28.0

# AI/ML
google-generativeai>=0.3.0

# Data Processing
beautifulsoup4>=4.12.0
pandas>=2.0.0
numpy>=1.24.0

# Utilities
python-dotenv>=1.0.0
requests>=2.31.0
aiohttp>=3.8.0
```

#### **Development Dependencies**
```txt
# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0

# Code Quality
black>=23.0.0
flake8>=6.0.0
mypy>=1.5.0

# Documentation
mkdocs>=1.5.0
mkdocs-material>=9.2.0
```

---

### **Configuration**

#### **Environment Variables**
```bash
# Required
GOOGLE_API_KEY=your_google_api_key_here

# Optional (for full functionality)
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
PINECONE_INDEX_NAME=mag7-financial-intelligence-2025

# SEC Scraper
SEC_USER_AGENT=Student Research your_email@domain.com

# Application
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
LOG_LEVEL=INFO
```

#### **Configuration Files**
- `.env`: Environment variables (not in version control)
- `env.example`: Environment variables template
- `requirements.txt`: Python dependencies
- `Makefile`: Build and deployment commands

---

## 🔧 **Development Workflows**

### **Local Development**

#### **Setting Up Development Environment**
```bash
# Clone and setup
git clone <repository-url>
cd unique
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install
```

#### **Development Commands**
```bash
# Run web interface
streamlit run app.py

# Run CLI interface
python cli_app.py

# Run tests
pytest

# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .

# Process SEC filings
python -c "from data_storing.text_cleaning import SECTextProcessor; processor = SECTextProcessor(); processor.process_all_filings()"

# Upload to Pinecone
python storing_vector_db/upload_to_pinecone.py
```

#### **Code Style Guidelines**
- **Python**: Follow PEP 8 with Black formatting
- **Docstrings**: Use Google-style docstrings
- **Type Hints**: Use type hints for all functions
- **Error Handling**: Use try-except with specific exception types
- **Logging**: Use structured logging with appropriate levels

#### **Example Code Structure**
```python
"""
Module for processing SEC filing data.

This module provides utilities for cleaning and processing SEC filing HTML files
into structured chunks suitable for vector database storage.
"""

import logging
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class SECTextProcessor:
    """Process SEC filing HTML files into structured chunks."""
    
    def __init__(self, data_dir: str = "sec_filings_data"):
        """Initialize the SEC text processor.
        
        Args:
            data_dir: Directory containing SEC filing data
        """
        self.data_dir = Path(data_dir)
        self.processed_dir = Path("processed_filings")
        self.processed_dir.mkdir(exist_ok=True)
    
    def process_all_filings(self) -> Dict[str, int]:
        """Process all SEC filings in the data directory.
        
        Returns:
            Dictionary with processing statistics
        """
        try:
            # Implementation here
            pass
        except Exception as e:
            logger.error(f"Error processing filings: {e}")
            raise
```

---

### **Testing**

#### **Test Structure**
```
tests/
├── test_conversational_agent.py    # Agent tests
├── test_vector_db.py              # Vector database tests
├── test_data_processing.py        # Data processing tests
├── test_web_interface.py          # Web interface tests
└── conftest.py                    # Test configuration
```

#### **Running Tests**
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_conversational_agent.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run async tests
pytest tests/ -v

# Run integration tests
pytest tests/ -m "integration"
```

#### **Test Examples**
```python
"""Tests for the conversational agent."""

import pytest
import asyncio
from conversational_agent import MAG7ConversationalAgent


class TestMAG7ConversationalAgent:
    """Test cases for MAG7ConversationalAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create a test agent instance."""
        return MAG7ConversationalAgent()
    
    @pytest.mark.asyncio
    async def test_process_message_general_query(self, agent):
        """Test processing a general query."""
        result = await agent.process_message("test_conv", "Hello")
        
        assert result["response"] is not None
        assert result["confidence"] > 0
        assert result["query_type"] == "GENERAL_QUERY"
    
    @pytest.mark.asyncio
    async def test_process_message_financial_query(self, agent):
        """Test processing a financial query."""
        result = await agent.process_message(
            "test_conv", 
            "What was Microsoft's revenue in 2024?"
        )
        
        assert result["response"] is not None
        assert result["confidence"] > 0
        assert result["query_type"] in ["FINANCIAL_RAG", "GENERAL_QUERY"]
```

---

### **Debugging**

#### **Debug Configuration**
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Debug environment variables
import os
from dotenv import load_dotenv
load_dotenv()
print(f"GOOGLE_API_KEY: {'SET' if os.getenv('GOOGLE_API_KEY') else 'NOT SET'}")
print(f"PINECONE_API_KEY: {'SET' if os.getenv('PINECONE_API_KEY') else 'NOT SET'}")
```

#### **Common Debug Scenarios**

1. **API Key Issues**
```python
# Test Google API
import google.generativeai as genai
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash-latest')
response = model.generate_content("Hello")
print(response.text)
```

2. **Pinecone Connection Issues**
```python
# Test Pinecone connection
import pinecone
pinecone.init(api_key=os.getenv("PINECONE_API_KEY"))
print(pinecone.list_indexes())
```

3. **LlamaIndex Workflow Issues**
```python
# Test workflow step
from conversational_agent import MAG7FinancialWorkflow
workflow = MAG7FinancialWorkflow()
result = await workflow.classify_query("What was Apple's revenue?")
print(result)
```

---

### **Code Quality**

#### **Pre-commit Hooks**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.9
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
```

#### **Code Review Checklist**
- [ ] Code follows style guidelines
- [ ] Type hints are used
- [ ] Docstrings are present
- [ ] Error handling is appropriate
- [ ] Tests are written
- [ ] No hardcoded credentials
- [ ] Logging is implemented
- [ ] Performance considerations

---

## 📦 **Deployment**

### **Docker Deployment**

#### **Dockerfile**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Set environment variables
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Run the application
CMD ["streamlit", "run", "app.py"]
```

#### **Docker Compose**
```yaml
# docker-compose.yml
version: '3.8'

services:
  mag7-app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - PINECONE_API_KEY=${PINECONE_API_KEY}
      - PINECONE_INDEX_NAME=${PINECONE_INDEX_NAME}
    volumes:
      - ./processed_filings:/app/processed_filings
      - ./sec_filings_data:/app/sec_filings_data
    restart: unless-stopped
```

#### **Deployment Commands**
```bash
# Build and run with Docker
docker build -t mag7-financial-intelligence .
docker run -p 8501:8501 --env-file .env mag7-financial-intelligence

# Or use Docker Compose
docker-compose up -d
```

---

### **Production Setup**

#### **Environment Configuration**
```bash
# Production environment variables
GOOGLE_API_KEY=your_production_google_key
PINECONE_API_KEY=your_production_pinecone_key
PINECONE_INDEX_NAME=mag7-financial-intelligence-prod
LOG_LEVEL=WARNING
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

#### **Security Considerations**
- Use environment variables for all secrets
- Implement rate limiting
- Add authentication if needed
- Use HTTPS in production
- Regular security updates

#### **Performance Optimization**
- Enable caching for vector database queries
- Use connection pooling
- Implement request queuing
- Monitor resource usage

---

### **Monitoring**

#### **Logging Configuration**
```python
import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler('app.log', maxBytes=1024*1024, backupCount=5),
            logging.StreamHandler(sys.stdout)
        ]
    )
```

#### **Health Checks**
```python
def health_check():
    """Perform system health check."""
    checks = {
        "google_api": check_google_api(),
        "pinecone_api": check_pinecone_api(),
        "vector_database": check_vector_database(),
        "data_files": check_data_files()
    }
    return all(checks.values()), checks
```

---

## 🔍 **Troubleshooting**

### **Common Issues**

#### **1. Import Errors**
```bash
# Error: ModuleNotFoundError: No module named 'llama_index'
# Solution: Install modular packages
pip uninstall llama-index
pip install llama-index-core llama-index-embeddings-gemini llama-index-llms-gemini llama-index-workflow
```

#### **2. API Key Errors**
```bash
# Error: 401 Unauthorized
# Solution: Check API keys
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('GOOGLE_API_KEY:', 'SET' if os.getenv('GOOGLE_API_KEY') else 'NOT SET')"
```

#### **3. Pinecone Index Errors**
```bash
# Error: Index not found
# Solution: Create index
python -c "from storing_vector_db.embeddings import create_pinecone_index; create_pinecone_index('mag7-financial-intelligence-2025')"
```

#### **4. Memory Issues**
```bash
# Error: Out of memory
# Solution: Reduce batch size
python storing_vector_db/upload_to_pinecone.py --batch-size 50
```

---

### **Performance Optimization**

#### **Vector Database Optimization**
```python
# Use smaller batch sizes for large datasets
BATCH_SIZE = 50  # Instead of 100

# Implement caching
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_query(query: str, top_k: int = 5):
    return query_pinecone(query, top_k=top_k)
```

#### **Memory Management**
```python
# Process files in chunks
def process_large_file(file_path: str, chunk_size: int = 1000):
    with open(file_path, 'r') as f:
        for chunk in iter(lambda: list(islice(f, chunk_size)), []):
            process_chunk(chunk)
```

---

### **Security Considerations**

#### **API Key Security**
```python
# Never hardcode API keys
# Use environment variables
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not set")
```

#### **Input Validation**
```python
# Validate user input
import re

def validate_query(query: str) -> bool:
    """Validate user query input."""
    if not query or len(query) > 1000:
        return False
    # Add more validation as needed
    return True
```

#### **Rate Limiting**
```python
# Implement rate limiting
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests: int = 100, window: int = 3600):
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)
    
    def is_allowed(self, user_id: str) -> bool:
        now = time.time()
        user_requests = self.requests[user_id]
        user_requests = [req for req in user_requests if now - req < self.window]
        self.requests[user_id] = user_requests
        return len(user_requests) < self.max_requests
```

---

## 📚 **Additional Resources**

### **Documentation**
- [CODEBASE_INDEX.md](CODEBASE_INDEX.md) - Comprehensive code index
- [FUNCTION_INDEX.md](FUNCTION_INDEX.md) - Function reference guide
- [API_REFERENCE.md](API_REFERENCE.md) - API documentation
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick start guide

### **External Resources**
- [LlamaIndex Documentation](https://docs.llamaindex.ai/)
- [Pinecone Documentation](https://docs.pinecone.io/)
- [Google AI Documentation](https://ai.google.dev/)
- [Streamlit Documentation](https://docs.streamlit.io/)

### **Community**
- [GitHub Issues](https://github.com/your-repo/issues)
- [Discussions](https://github.com/your-repo/discussions)
- [Contributing Guidelines](CONTRIBUTING.md)

---

*Last Updated: June 21, 2025*
*Version: 2.0 - Modern Pinecone Integration* 