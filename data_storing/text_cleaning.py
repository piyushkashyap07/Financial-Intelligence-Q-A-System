import json
import re
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
from dataclasses import dataclass, asdict
import hashlib

# HTML parsing
from bs4 import BeautifulSoup, Comment
import html

# Text processing
import unicodedata
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class DocumentChunk:
    """Represents a processed document chunk with metadata"""
    chunk_id: str
    company: str
    form_type: str
    filing_date: str
    report_date: str
    accession_number: str
    section: str
    subsection: Optional[str]
    text: str
    word_count: int
    char_count: int
    chunk_index: int
    source_file: str
    page_number: Optional[int] = None
    table_data: Optional[Dict] = None
    
class SECTextProcessor:
    """
    Advanced SEC filing text extractor and preprocessor
    Converts HTML filings to structured JSON with intelligent chunking
    """
    
    def __init__(self, 
                 input_dir: str = "sec_filings_data",
                 output_dir: str = "processed_filings",
                 chunk_size: int = 800,
                 chunk_overlap: int = 100,
                 min_chunk_size: int = 200):
        """
        Initialize the text processor
        
        Args:
            input_dir: Directory containing raw SEC filings
            output_dir: Directory to save processed JSON files
            chunk_size: Target chunk size in tokens (roughly)
            chunk_overlap: Overlap between chunks in tokens
            min_chunk_size: Minimum chunk size to keep
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # SEC filing section patterns
        self.section_patterns = {
            # 10-K sections
            'ITEM 1': r'(?i)\b(?:item\s+1\b|item\s+1\.)\s*(?:business|description\s+of\s+business)',
            'ITEM 1A': r'(?i)\b(?:item\s+1a\b|item\s+1\.a\.?)\s*(?:risk\s+factors)',
            'ITEM 2': r'(?i)\b(?:item\s+2\b|item\s+2\.)\s*(?:properties)',
            'ITEM 3': r'(?i)\b(?:item\s+3\b|item\s+3\.)\s*(?:legal\s+proceedings)',
            'ITEM 4': r'(?i)\b(?:item\s+4\b|item\s+4\.)\s*(?:mine\s+safety|controls\s+and\s+procedures)',
            'ITEM 5': r'(?i)\b(?:item\s+5\b|item\s+5\.)\s*(?:market\s+for|unregistered\s+sales)',
            'ITEM 6': r'(?i)\b(?:item\s+6\b|item\s+6\.)\s*(?:selected\s+financial\s+data)',
            'ITEM 7': r'(?i)\b(?:item\s+7\b|item\s+7\.)\s*(?:management.?s\s+discussion|md&a)',
            'ITEM 7A': r'(?i)\b(?:item\s+7a\b|item\s+7\.a\.?)\s*(?:quantitative\s+and\s+qualitative)',
            'ITEM 8': r'(?i)\b(?:item\s+8\b|item\s+8\.)\s*(?:financial\s+statements)',
            'ITEM 9': r'(?i)\b(?:item\s+9\b|item\s+9\.)\s*(?:changes\s+in\s+and\s+disagreements)',
            'ITEM 9A': r'(?i)\b(?:item\s+9a\b|item\s+9\.a\.?)\s*(?:controls\s+and\s+procedures)',
            'ITEM 10': r'(?i)\b(?:item\s+10\b|item\s+10\.)\s*(?:directors|executive\s+officers)',
            'ITEM 11': r'(?i)\b(?:item\s+11\b|item\s+11\.)\s*(?:executive\s+compensation)',
            'ITEM 12': r'(?i)\b(?:item\s+12\b|item\s+12\.)\s*(?:security\s+ownership)',
            'ITEM 13': r'(?i)\b(?:item\s+13\b|item\s+13\.)\s*(?:certain\s+relationships)',
            'ITEM 14': r'(?i)\b(?:item\s+14\b|item\s+14\.)\s*(?:principal\s+accounting)',
            'ITEM 15': r'(?i)\b(?:item\s+15\b|item\s+15\.)\s*(?:exhibits|financial\s+statement)',
            'ITEM 16': r'(?i)\b(?:item\s+16\b|item\s+16\.)\s*(?:form\s+10-k\s+summary)',
            
            # 10-Q sections
            'PART I': r'(?i)\bpart\s+i\b',
            'PART II': r'(?i)\bpart\s+ii\b',
            'ITEM 1_Q': r'(?i)\b(?:item\s+1\b|item\s+1\.)\s*(?:financial\s+statements)',
            'ITEM 2_Q': r'(?i)\b(?:item\s+2\b|item\s+2\.)\s*(?:management.?s\s+discussion|md&a)',
            'ITEM 3_Q': r'(?i)\b(?:item\s+3\b|item\s+3\.)\s*(?:quantitative\s+and\s+qualitative)',
            'ITEM 4_Q': r'(?i)\b(?:item\s+4\b|item\s+4\.)\s*(?:controls\s+and\s+procedures)',
            'ITEM 5_Q': r'(?i)\b(?:item\s+5\b|item\s+5\.)\s*(?:other\s+information)',
            'ITEM 6_Q': r'(?i)\b(?:item\s+6\b|item\s+6\.)\s*(?:exhibits)',
            
            # General sections
            'REVENUE': r'(?i)\b(?:revenue|net\s+sales|total\s+revenue)\b',
            'COST_OF_REVENUE': r'(?i)\b(?:cost\s+of\s+revenue|cost\s+of\s+sales|cost\s+of\s+goods\s+sold)\b',
            'OPERATING_EXPENSES': r'(?i)\b(?:operating\s+expenses|operating\s+costs)\b',
            'R&D': r'(?i)\b(?:research\s+and\s+development|r&d)\b',
            'OPERATING_INCOME': r'(?i)\b(?:operating\s+income|income\s+from\s+operations)\b',
            'NET_INCOME': r'(?i)\b(?:net\s+income|net\s+earnings)\b',
            'CASH_FLOW': r'(?i)\b(?:cash\s+flow|cash\s+flows)\b',
            'BALANCE_SHEET': r'(?i)\b(?:balance\s+sheet|consolidated\s+balance\s+sheet)\b',
        }
        
        # Unwanted content patterns
        self.noise_patterns = [
            r'(?i)table\s+of\s+contents',
            r'(?i)page\s+\d+\s+of\s+\d+',
            r'(?i)exhibit\s+\d+',
            r'(?i)signature\s*$',
            r'(?i)pursuant\s+to\s+the\s+requirements',
            r'^\s*\d+\s*$',  # Page numbers
            r'^\s*-+\s*$',   # Separator lines
        ]
        
        # Financial keywords for enhanced metadata
        self.financial_keywords = {
            'revenue_terms': ['revenue', 'net sales', 'total revenue', 'sales', 'income'],
            'cost_terms': ['cost of revenue', 'cost of sales', 'cost of goods sold', 'cogs'],
            'expense_terms': ['operating expenses', 'research and development', 'r&d', 'sales and marketing', 'general and administrative'],
            'profit_terms': ['gross profit', 'operating income', 'net income', 'earnings', 'profit'],
            'cash_terms': ['cash flow', 'free cash flow', 'operating cash flow', 'cash and cash equivalents'],
            'balance_terms': ['total assets', 'total liabilities', 'shareholders equity', 'working capital'],
            'growth_terms': ['year-over-year', 'growth', 'increase', 'decrease', 'compared to'],
            'risk_terms': ['risk factors', 'uncertainty', 'competition', 'regulatory', 'market risk']
        }
    
    def clean_html(self, html_content: str) -> str:
        """
        Clean HTML content and extract text
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            Cleaned text content
        """
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove unwanted elements
        for element in soup.find_all(['script', 'style', 'meta', 'link', 'head']):
            element.decompose()
        
        # Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
        
        # Convert to text
        text = soup.get_text()
        
        # Clean up whitespace and special characters
        text = html.unescape(text)
        text = unicodedata.normalize('NFKD', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def extract_tables(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Extract and structure table data from HTML
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            List of structured table data
        """
        tables = []
        
        for i, table in enumerate(soup.find_all('table')):
            try:
                table_data = {
                    'table_id': i,
                    'headers': [],
                    'rows': [],
                    'caption': None
                }
                
                # Extract caption
                caption = table.find('caption')
                if caption:
                    table_data['caption'] = caption.get_text().strip()
                
                # Extract headers
                header_row = table.find('thead')
                if header_row:
                    headers = header_row.find_all(['th', 'td'])
                    table_data['headers'] = [h.get_text().strip() for h in headers]
                
                # Extract rows
                tbody = table.find('tbody') or table
                for row in tbody.find_all('tr'):
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        row_data = [cell.get_text().strip() for cell in cells]
                        table_data['rows'].append(row_data)
                
                if table_data['rows']:  # Only add non-empty tables
                    tables.append(table_data)
                    
            except Exception as e:
                logger.warning(f"Error extracting table {i}: {e}")
                continue
        
        return tables
    
    def identify_section(self, text: str) -> Tuple[str, Optional[str]]:
        """
        Identify the section and subsection of a text chunk
        
        Args:
            text: Text content to analyze
            
        Returns:
            Tuple of (section, subsection)
        """
        text_lower = text.lower()
        
        # Check for section patterns
        for section_name, pattern in self.section_patterns.items():
            if re.search(pattern, text_lower):
                # Try to find subsection
                subsection = None
                if 'item' in section_name.lower():
                    # Look for subsection patterns
                    subsection_match = re.search(r'(?i)(?:item\s+\d+[a-z]?\.?)\s*([^.]*)', text_lower)
                    if subsection_match:
                        subsection = subsection_match.group(1).strip()
                
                return section_name, subsection
        
        # Default section
        return 'GENERAL', None
    
    def is_noise_content(self, text: str) -> bool:
        """
        Check if text is noise content that should be filtered out
        
        Args:
            text: Text to check
            
        Returns:
            True if text is noise, False otherwise
        """
        text_lower = text.lower()
        
        # Check noise patterns
        for pattern in self.noise_patterns:
            if re.search(pattern, text_lower):
                return True
        
        # Check for very short content
        if len(text.strip()) < 50:
            return True
        
        # Check for mostly numbers/symbols
        if len(re.findall(r'[a-zA-Z]', text)) < len(text) * 0.3:
            return True
        
        return False
    
    def create_chunks(self, text: str, metadata: Dict) -> List[DocumentChunk]:
        """
        Create chunks from text with intelligent boundaries
        
        Args:
            text: Text to chunk
            metadata: Document metadata
            
        Returns:
            List of DocumentChunk objects
        """
        chunks = []
        
        # Split text into sentences first
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        current_chunk = ""
        chunk_index = 0
        
        for sentence in sentences:
            # Skip noise content
            if self.is_noise_content(sentence):
                continue
            
            # Check if adding this sentence would exceed chunk size
            if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                # Create chunk
                chunk = self._create_chunk_object(current_chunk, metadata, chunk_index)
                chunks.append(chunk)
                
                # Start new chunk with overlap
                overlap_sentences = current_chunk.split('. ')[-2:]  # Last 2 sentences
                current_chunk = '. '.join(overlap_sentences) + '. ' + sentence
                chunk_index += 1
            else:
                current_chunk += sentence + ' '
        
        # Add final chunk if it meets minimum size
        if len(current_chunk.strip()) >= self.min_chunk_size:
            chunk = self._create_chunk_object(current_chunk.strip(), metadata, chunk_index)
            chunks.append(chunk)
        
        return chunks
    
    def _create_chunk_object(self, text: str, metadata: Dict, chunk_index: int) -> DocumentChunk:
        """
        Create a DocumentChunk object from text and metadata
        
        Args:
            text: Chunk text
            metadata: Document metadata
            chunk_index: Index of this chunk
            
        Returns:
            DocumentChunk object
        """
        # Identify section
        section, subsection = self.identify_section(text)
        
        # Generate chunk ID
        chunk_id = self.generate_chunk_id(metadata, chunk_index)
        
        # Count words and characters
        word_count = len(text.split())
        char_count = len(text)
        
        return DocumentChunk(
            chunk_id=chunk_id,
            company=metadata.get('company', 'Unknown'),
            form_type=metadata.get('form_type', 'Unknown'),
            filing_date=metadata.get('filing_date', 'Unknown'),
            report_date=metadata.get('report_date', 'Unknown'),
            accession_number=metadata.get('accession_number', 'Unknown'),
            section=section,
            subsection=subsection,
            text=text,
            word_count=word_count,
            char_count=char_count,
            chunk_index=chunk_index,
            source_file=metadata.get('source_file', 'Unknown')
        )
    
    def generate_chunk_id(self, metadata: Dict, chunk_index: int) -> str:
        """
        Generate a unique chunk ID
        
        Args:
            metadata: Document metadata
            chunk_index: Chunk index
            
        Returns:
            Unique chunk ID
        """
        # Create a hash from metadata and chunk index
        hash_input = f"{metadata.get('company', '')}_{metadata.get('filing_date', '')}_{metadata.get('form_type', '')}_{chunk_index}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]
    
    def extract_metadata_from_filename(self, filename: str) -> Dict:
        """
        Extract metadata from SEC filing filename
        
        Args:
            filename: SEC filing filename
            
        Returns:
            Dictionary of metadata
        """
        # Example filename: AAPL10-K2023-10-27_0000320193-23-000106.html
        metadata = {}
        
        try:
            # Extract company ticker
            company_match = re.match(r'^([A-Z]+)', filename)
            if company_match:
                metadata['company'] = company_match.group(1)
            
            # Extract form type (10-K, 10-Q, etc.)
            form_match = re.search(r'(10-[KQ])', filename)
            if form_match:
                metadata['form_type'] = form_match.group(1)
            
            # Extract filing date
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
            if date_match:
                metadata['filing_date'] = date_match.group(1)
            
            # Extract accession number
            acc_match = re.search(r'_(\d{10}-\d{2}-\d{6})_', filename)
            if acc_match:
                metadata['accession_number'] = acc_match.group(1)
            
            # Set report date (usually same as filing date for now)
            metadata['report_date'] = metadata.get('filing_date', 'Unknown')
            
            # Set source file
            metadata['source_file'] = filename
            
        except Exception as e:
            logger.warning(f"Error extracting metadata from filename {filename}: {e}")
            metadata = {
                'company': 'Unknown',
                'form_type': 'Unknown',
                'filing_date': 'Unknown',
                'report_date': 'Unknown',
                'accession_number': 'Unknown',
                'source_file': filename
            }
        
        return metadata
    
    def process_single_filing(self, file_path: Path) -> Dict:
        """
        Process a single SEC filing
        
        Args:
            file_path: Path to the HTML filing
            
        Returns:
            Dictionary with processing results
        """
        try:
            logger.info(f"Processing {file_path.name}")
            
            # Read HTML content
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Clean HTML and extract text
            text = self.clean_html(html_content)
            
            # Extract metadata from filename
            metadata = self.extract_metadata_from_filename(file_path.name)
            
            # Create chunks
            chunks = self.create_chunks(text, metadata)
            
            # Convert chunks to dictionaries
            chunk_dicts = [asdict(chunk) for chunk in chunks]
            
            # Create output structure
            result = {
                'filename': file_path.name,
                'metadata': metadata,
                'chunks': chunk_dicts,
                'total_chunks': len(chunks),
                'total_words': sum(chunk.word_count for chunk in chunks),
                'processing_timestamp': datetime.now().isoformat()
            }
            
            # Save to JSON file
            output_file = self.output_dir / f"{file_path.stem}_processed.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Processed {file_path.name}: {len(chunks)} chunks")
            return result
            
        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {e}")
            return {
                'filename': file_path.name,
                'error': str(e),
                'processing_timestamp': datetime.now().isoformat()
            }
    
    def process_all_filings(self) -> Dict:
        """
        Process all SEC filings in the input directory
        
        Returns:
            Dictionary with processing summary
        """
        logger.info(f"Starting to process filings from {self.input_dir}")
        
        # Find all HTML files
        html_files = list(self.input_dir.rglob("*.html"))
        
        if not html_files:
            logger.warning(f"No HTML files found in {self.input_dir}")
            return {'error': 'No HTML files found'}
        
        logger.info(f"Found {len(html_files)} HTML files to process")
        
        # Process each file
        results = []
        successful = 0
        failed = 0
        
        for file_path in html_files:
            result = self.process_single_filing(file_path)
            results.append(result)
            
            if 'error' in result:
                failed += 1
            else:
                successful += 1
        
        # Create summary
        summary = {
            'total_files': len(html_files),
            'successful': successful,
            'failed': failed,
            'results': results,
            'processing_timestamp': datetime.now().isoformat()
        }
        
        # Save summary
        summary_file = self.output_dir / "processing_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Processing complete: {successful} successful, {failed} failed")
        return summary

def clean_text_for_query(query: str) -> str:
    """
    Clean and prepare a user query for vector search.
    This function provides the interface expected by the conversational agent.
    
    Args:
        query: Raw user query
        
    Returns:
        Cleaned query string optimized for vector search
    """
    if not query:
        return ""
    
    # Convert to string if needed
    query = str(query)
    
    # Remove extra whitespace
    query = re.sub(r'\s+', ' ', query.strip())
    
    # Remove special characters that might interfere with search
    query = re.sub(r'[^\w\s\-\.\,\?\!]', '', query)
    
    # Normalize unicode
    query = unicodedata.normalize('NFKD', query)
    
    # Convert to lowercase for consistency
    query = query.lower()
    
    # Remove common stop words that don't add semantic value
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
    }
    
    words = query.split()
    filtered_words = [word for word in words if word not in stop_words]
    
    # Reconstruct query
    cleaned_query = ' '.join(filtered_words)
    
    # Ensure minimum length
    if len(cleaned_query) < 3:
        return query  # Return original if cleaned version is too short
    
    return cleaned_query

def main():
    """Main function to run the text processor"""
    processor = SECTextProcessor()
    summary = processor.process_all_filings()
    
    print("Processing Summary:")
    print(f"Total files: {summary.get('total_files', 0)}")
    print(f"Successful: {summary.get('successful', 0)}")
    print(f"Failed: {summary.get('failed', 0)}")
    
    if 'error' in summary:
        print(f"Error: {summary['error']}")

if __name__ == "__main__":
    main()