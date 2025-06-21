.PHONY: setup run build docker-run docker-build clean test help

# Default target
help:
	@echo "MAG7 Financial Intelligence Q&A System"
	@echo "======================================"
	@echo "Available commands:"
	@echo "  setup       - Install dependencies and setup environment"
	@echo "  run         - Run the Streamlit web application"
	@echo "  cli         - Run the CLI version (LlamaIndex workflow)"
	@echo "  build       - Build Docker image"
	@echo "  docker-run  - Run with Docker Compose"
	@echo "  clean       - Clean up generated files"
	@echo "  test        - Run test scripts"
	@echo "  test-llamaindex - Test LlamaIndex workflow agent"
	@echo "  scrape      - Download SEC filings"
	@echo "  process     - Process filings into chunks"
	@echo "  upload      - Upload chunks to vector database"
	@echo "  workflow    - Test LlamaIndex workflow agent"

# Setup environment
setup:
	@echo "Setting up MAG7 Financial Intelligence Q&A System..."
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	@echo "Setup complete! Activate virtual environment with: source venv/bin/activate"

# Run Streamlit web app
run:
	@echo "Starting Streamlit web application..."
	streamlit run app.py

# Run CLI version
cli:
	@echo "Starting CLI version with LlamaIndex workflow..."
	python cli_app.py

# Test LlamaIndex workflow
workflow:
	@echo "Testing LlamaIndex workflow agent..."
	python -c "import asyncio; from conversational_agent import mag7_agent; print('Agent initialized successfully')"

# Build Docker image
build:
	@echo "Building Docker image..."
	docker build -t mag7-financial-qa .

# Run with Docker Compose
docker-run:
	@echo "Starting with Docker Compose..."
	docker-compose up -d

# Stop Docker Compose
docker-stop:
	@echo "Stopping Docker Compose..."
	docker-compose down

# Clean up generated files
clean:
	@echo "Cleaning up generated files..."
	rm -rf __pycache__
	rm -rf */__pycache__
	rm -rf .pytest_cache
	rm -rf .streamlit
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*.pyd" -delete

# Run tests
test:
	@echo "Running tests..."
	python test_sec_download.py
	python test_filename_parsing.py

# Test LlamaIndex workflow agent
test-llamaindex:
	@echo "Testing LlamaIndex workflow agent..."
	python test_llamaindex_agent.py

# Download SEC filings
scrape:
	@echo "Downloading SEC filings..."
	python -c "from data_storing.sec_data import SECFilingScraper; scraper = SECFilingScraper(); scraper.scrape_all_filings()"

# Process filings
process:
	@echo "Processing filings into chunks..."
	python -c "from data_storing.text_cleaning import SECTextProcessor; processor = SECTextProcessor(); processor.process_all_filings()"

# Upload to vector database
upload:
	@echo "Uploading chunks to vector database..."
	python storing_vector_db/upload_to_pinecone.py

# Full pipeline
pipeline: scrape process upload
	@echo "Full pipeline completed!"

# Development setup
dev-setup: setup
	@echo "Setting up development environment..."
	pip install black flake8 pytest
	@echo "Development setup complete!"

# Format code
format:
	@echo "Formatting code..."
	black .
	flake8 .

# Check system status
status:
	@echo "System Status:"
	@echo "=============="
	@echo "Python version:"
	python --version
	@echo "Installed packages:"
	pip list
	@echo "Environment variables:"
	@echo "PINECONE_API_KEY: $(if $(PINECONE_API_KEY),SET,NOT SET)"
	@echo "GOOGLE_API_KEY: $(if $(GOOGLE_API_KEY),SET,NOT SET)"
	@echo "PINECONE_INDEX_NAME: $(if $(PINECONE_INDEX_NAME),$(PINECONE_INDEX_NAME),mag7-financial-intelligence-2025)"

# Quick test of the system
quick-test:
	@echo "Running quick system test..."
	@echo "Testing LlamaIndex workflow agent..."
	python -c "import asyncio; from conversational_agent import mag7_agent; print('✅ LlamaIndex agent loaded successfully')"
	@echo "Testing vector database connection..."
	python -c "from storing_vector_db.retrieval import get_relevant_chunks; print('✅ Vector database connection ready')"
	@echo "Testing text processing..."
	python -c "from data_storing.text_cleaning import clean_text_for_query; print('✅ Text processing ready')"
	@echo "All systems ready!" 