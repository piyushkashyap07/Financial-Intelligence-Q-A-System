# SEC Filing Data Processing System - Quick Reference

## 🚀 Quick Start Commands

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Download SEC Filings
```python
from data_storing.sec_data import SECFilingScraper

# Initialize scraper (user agent required)
scraper = SECFilingScraper(user_agent="YourCompany contact@yourcompany.com")

# Download all filings
results = scraper.scrape_all_filings()
```

### 3. Process Filings
```python
from data_storing.text_cleaning import SECTextProcessor

# Initialize processor
processor = SECTextProcessor()

# Process all filings
results = processor.process_all_filings()
```

### 4. Upload to Vector Database
```python
from storing_vector_db.embeddings import load_and_upload_all_chunks

# Upload processed chunks
result = load_and_upload_all_chunks(
    "processed_filings/all_chunks.json", 
    "mag7-financial-intelligence-2025"
)
```

### 5. Query the System
```python
from storing_vector_db.retrieval import rag_answer

# Ask questions
response = rag_answer("What was Microsoft's revenue for Q1 2024?")
print(response["answer"])
```

## 📋 Configuration Quick Reference

### Environment Variables
```bash
# Required for vector database
PINECONE_API_KEY=your_pinecone_key
GOOGLE_API_KEY=your_google_key
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
```

### Scraper Configuration
```python
scraper = SECFilingScraper(
    user_agent="YourCompany contact@yourcompany.com"  # Required
)

# Optional customizations
scraper.start_date = "2020-01-01"      # Date range
scraper.end_date = "2024-12-31"
scraper.filing_types = ["10-K"]        # Only annual reports
scraper.rate_limit_delay = 0.2         # 5 requests per second
```

### Processor Configuration
```python
processor = SECTextProcessor(
    chunk_size=800,      # Target chunk size in tokens
    chunk_overlap=100,   # Overlap between chunks
    min_chunk_size=200   # Minimum chunk size to keep
)
```

## 🎯 Target Companies (MAG7)

| Company | Symbol | CIK | Filing Types |
|---------|--------|-----|--------------|
| Apple Inc | AAPL | 320193 | 10-K, 10-Q |
| Microsoft Corporation | MSFT | 789019 | 10-K, 10-Q |
| Amazon.com Inc | AMZN | 1018724 | 10-K, 10-Q |
| Alphabet Inc | GOOGL | 1652044 | 10-K, 10-Q |
| Meta Platforms Inc | META | 1326801 | 10-K, 10-Q |
| NVIDIA Corporation | NVDA | 1045810 | 10-K, 10-Q |
| Tesla Inc | TSLA | 1318605 | 10-K, 10-Q |

## 📊 Data Access Examples

### Load Processed Data
```python
import json

# Load all chunks
with open('processed_filings/all_chunks.json', 'r') as f:
    chunks = json.load(f)

# Filter by company
aapl_chunks = [chunk for chunk in chunks if chunk['company'] == 'AAPL']

# Filter by section
md_and_a = [chunk for chunk in chunks if chunk['section'] == 'ITEM 7']
risk_factors = [chunk for chunk in chunks if chunk['section'] == 'ITEM 1A']
```

### Get Filing Statistics
```python
# After scraping
stats = scraper.get_filing_statistics(all_filings)
print(f"Total filings: {stats['total_filings']}")
print(f"By company: {stats['by_company']}")
```

## 🔍 Section Identification

### 10-K Sections
- `ITEM 1` - Business description
- `ITEM 1A` - Risk factors
- `ITEM 7` - Management discussion (MD&A)
- `ITEM 8` - Financial statements
- `ITEM 9` - Changes in disagreements
- `ITEM 10` - Directors and officers
- `ITEM 11` - Executive compensation
- `ITEM 12` - Security ownership
- `ITEM 13` - Certain relationships
- `ITEM 14` - Principal accounting
- `ITEM 15` - Exhibits

### 10-Q Sections
- `PART I` - Financial information
- `PART II` - Other information
- `ITEM 2` - Management discussion
- `ITEM 3` - Quantitative disclosures
- `ITEM 4` - Controls and procedures
- `ITEM 5` - Other information
- `ITEM 6` - Exhibits

### Financial Categories
- `REVENUE` - Revenue-related content
- `COST_OF_REVENUE` - Cost of sales
- `OPERATING_EXPENSES` - Operating costs
- `R&D` - Research and development
- `OPERATING_INCOME` - Operating income
- `NET_INCOME` - Profit/loss information
- `CASH_FLOW` - Cash flow statements
- `BALANCE_SHEET` - Balance sheet data

## 🛠️ Common Operations

### Test Single Filing Download
```python
# Test with specific company and date
scraper.test_single_filing_download("AAPL", "2023-11-03")
```

### Test Filename Parsing
```python
# Run filename parsing test
python test_filename_parsing.py
```

### Vector Search Only
```python
from storing_vector_db.retrieval import query_pinecone

results = query_pinecone(
    "What was Microsoft's revenue?", 
    "mag7-financial-intelligence-2025", 
    top_k=5
)

for r in results:
    print(f"{r['company']} {r['form_type']} {r['filing_date']} | Score: {r['score']}")
    print(r['text'][:300], "...\n")
```

### Filtered Search
```python
# Search only Apple filings
filter_dict = {"company": "AAPL"}
results = query_pinecone(
    "iPhone sales", 
    "mag7-financial-intelligence-2025", 
    filter_dict=filter_dict
)
```

## 🚨 Troubleshooting

### Common Issues and Solutions

#### Scraper Issues

**Problem**: No files downloaded
```python
# Solution: Check user agent and network
scraper = SECFilingScraper(user_agent="YourCompany contact@yourcompany.com")
# Ensure proper user agent format
```

**Problem**: Rate limiting errors
```python
# Solution: Increase delay
scraper.rate_limit_delay = 0.2  # 5 requests per second
```

**Problem**: Missing companies
```python
# Solution: Verify CIK numbers
print(scraper.companies)  # Check CIK mapping
```

#### Processor Issues

**Problem**: Empty chunks
```python
# Solution: Check minimum chunk size
processor = SECTextProcessor(min_chunk_size=100)
```

**Problem**: Memory errors
```python
# Solution: Reduce chunk size
processor = SECTextProcessor(chunk_size=500)
```

**Problem**: Encoding errors
```python
# Solution: Files are processed with errors='ignore'
# Check file encoding manually if needed
```

#### Vector Database Issues

**Problem**: API key errors
```bash
# Solution: Set environment variables
export PINECONE_API_KEY=your_key
export GOOGLE_API_KEY=your_key
```

**Problem**: Index not found
```python
# Solution: Create index first
from storing_vector_db.embeddings import create_pinecone_index
index = create_pinecone_index("mag7-financial-intelligence-2025", 768)
```

**Problem**: Large chunk errors
```python
# Solution: Check chunk size limits
# Maximum chunk size: ~35,000 bytes for API safety
```

### Performance Tuning

#### For Large Datasets
```python
processor = SECTextProcessor(
    chunk_size=500,      # Smaller chunks
    min_chunk_size=100   # Lower minimum
)
```

#### For Faster Processing
```python
processor = SECTextProcessor(
    chunk_size=1500,
    chunk_overlap=50
)
```

#### For Better Search Results
```python
# Increase top_k for more context
response = rag_answer(
    "What was Microsoft's revenue?", 
    top_k=10  # More chunks for context
)
```

## 📈 Data Statistics

### Expected File Sizes
- Raw HTML files: ~50-200MB per company per year
- Processed JSON: ~10-50MB per company per year
- Vector embeddings: ~1-5MB per company per year

### Processing Speed
- Download: ~1-2 filings per minute (rate limited)
- Text processing: ~10-50 filings per minute
- Embedding generation: ~100-500 chunks per minute

### Storage Requirements
- Total raw data: ~2-8GB for MAG7 (2015-2025)
- Total processed data: ~500MB-2GB
- Vector database: ~50-200MB

## 🔒 Security & Compliance

### SEC Requirements
- **User Agent**: Required for API access
- **Rate Limiting**: Maximum 10 requests per second
- **Terms of Service**: Must comply with SEC terms

### Best Practices
- Use descriptive user agent with contact information
- Implement proper error handling
- Log all operations for audit trail
- Respect rate limits

## 📞 Support Commands

### Check System Status
```python
# Check if files exist
import os
print(f"Raw filings: {len(os.listdir('sec_filings_data'))}")
print(f"Processed files: {len(os.listdir('processed_filings'))}")

# Check Pinecone index
from storing_vector_db.embeddings import create_pinecone_index
index = create_pinecone_index("mag7-financial-intelligence-2025")
print(f"Index stats: {index.describe_index_stats()}")
```

### Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
# Run your operations with detailed logging
```

### Validate Data
```python
# Check chunk quality
with open('processed_filings/all_chunks.json', 'r') as f:
    chunks = json.load(f)

print(f"Total chunks: {len(chunks)}")
print(f"Companies: {set(chunk['company'] for chunk in chunks)}")
print(f"Sections: {set(chunk['section'] for chunk in chunks)}")
```

---

**Quick Links**:
- [CODEBASE_INDEX.md](CODEBASE_INDEX.md) - Comprehensive codebase documentation
- [FUNCTION_INDEX.md](FUNCTION_INDEX.md) - Detailed function-level documentation
- [README.md](README.md) - Main project documentation

For detailed troubleshooting and advanced usage, refer to the main documentation files. 