import requests
import json
import time
import os
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Optional
import re
from urllib.parse import urljoin
import pandas as pd
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SECFilingScraper:
    """
    Automated SEC filing scraper for MAG7 companies
    Downloads 10-K and 10-Q filings from 2015-2025
    """
    
    def __init__(self, user_agent: str = "YourCompany contact@yourcompany.com"):
        """
        Initialize the scraper with required user agent for SEC API
        
        Args:
            user_agent: Required user agent string for SEC API compliance
        """
        self.base_url = "https://data.sec.gov/api/xbrl/companyconcept/"
        self.submissions_url = "https://data.sec.gov/submissions/"
        self.filing_url = "https://www.sec.gov/Archives/edgar/data/"
        
        # SEC requires user agent for API access
        self.api_headers = {
            "User-Agent": user_agent,
            "Accept-Encoding": "gzip, deflate",
            "Host": "data.sec.gov"
        }
        
        # Headers for filing downloads
        self.filing_headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        # MAG7 companies with their CIK numbers (Central Index Key)
        self.companies = {
            "AAPL": "320193",      # Apple Inc
            "MSFT": "789019",      # Microsoft Corporation  
            "AMZN": "1018724",     # Amazon.com Inc
            "GOOGL": "1652044",    # Alphabet Inc (Class A)
            "META": "1326801",     # Meta Platforms Inc
            "NVDA": "1045810",     # NVIDIA Corporation
            "TSLA": "1318605"      # Tesla Inc
        }
        
        # Target filing types
        self.filing_types = ["10-K", "10-Q"]
        
        # Date range
        self.start_date = "2015-01-01"
        self.end_date = "2025-12-31"
        
        # Rate limiting (SEC allows 10 requests per second)
        self.rate_limit_delay = 0.1
        
        # Create data directory
        self.data_dir = Path("sec_filings_data")
        self.data_dir.mkdir(exist_ok=True)
        
    def get_company_submissions(self, cik: str) -> Dict:
        """
        Get all submissions for a company using SEC submissions API
        
        Args:
            cik: Company's Central Index Key
            
        Returns:
            Dictionary containing company submissions data
        """
        # Pad CIK to 10 digits
        cik_padded = cik.zfill(10)
        url = f"{self.submissions_url}CIK{cik_padded}.json"
        
        try:
            logger.info(f"Fetching submissions from: {url}")
            response = requests.get(url, headers=self.api_headers)
            response.raise_for_status()
            time.sleep(self.rate_limit_delay)
            
            data = response.json()
            
            # Debug: Log the structure of the response
            logger.debug(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            if isinstance(data, dict) and 'filings' in data:
                logger.debug(f"Filings keys: {list(data['filings'].keys())}")
                if 'recent' in data['filings']:
                    logger.debug(f"Recent filings keys: {list(data['filings']['recent'].keys())}")
            
            return data
        except requests.RequestException as e:
            logger.error(f"Error fetching submissions for CIK {cik}: {e}")
            return {}
    
    def filter_filings(self, submissions: Dict, company_symbol: str) -> List[Dict]:
        """
        Filter submissions to get only 10-K and 10-Q filings within date range
        
        Args:
            submissions: Company submissions data from SEC API
            company_symbol: Company stock symbol
            
        Returns:
            List of filtered filing dictionaries
        """
        if not submissions or 'filings' not in submissions:
            logger.warning(f"No filings data found in submissions for {company_symbol}")
            return []
        
        filings = submissions['filings']['recent']
        filtered_filings = []
        
        # Debug: Log available keys in filings
        logger.debug(f"Available keys in filings: {list(filings.keys())}")
        
        # Check if required fields exist
        required_fields = ['form', 'filingDate', 'accessionNumber', 'primaryDocument', 'reportDate']
        missing_fields = [field for field in required_fields if field not in filings]
        if missing_fields:
            logger.error(f"Missing required fields in filings data: {missing_fields}")
            logger.error(f"Available fields: {list(filings.keys())}")
            return []
        
        for i in range(len(filings['form'])):
            form_type = filings['form'][i]
            filing_date = filings['filingDate'][i]
            
            # Check if it's a target filing type
            if form_type in self.filing_types:
                # Check if within date range
                if self.start_date <= filing_date <= self.end_date:
                    filing_info = {
                        'company': company_symbol,
                        'form_type': form_type,
                        'filing_date': filing_date,
                        'accession_number': filings['accessionNumber'][i],
                        'primary_document': filings['primaryDocument'][i],
                        'report_date': filings['reportDate'][i],
                        'cik': filings.get('cik', [None] * len(filings['form']))[i] if 'cik' in filings else None
                    }
                    filtered_filings.append(filing_info)
        
        return filtered_filings
    
    def construct_filing_url(self, filing_info: Dict) -> str:
        """
        Construct the direct URL to the filing document with fallback strategies
        
        Args:
            filing_info: Dictionary containing filing information
            
        Returns:
            Direct URL to the filing document
        """
        # Use CIK from filing_info if available, otherwise use the company's CIK
        cik = filing_info.get('cik')
        if cik is None:
            # Fallback to company's CIK from our mapping
            company_symbol = filing_info['company']
            cik = self.companies.get(company_symbol)
            if cik is None:
                raise ValueError(f"No CIK found for company {company_symbol}")
        
        cik = str(cik)
        accession_number = filing_info['accession_number'].replace('-', '')
        primary_document = filing_info['primary_document']
        
        # Try multiple URL patterns for SEC filings
        url_patterns = []
        
        # Pattern 1: Use the primary_document as provided
        if primary_document:
            url_patterns.append(f"{self.filing_url}{cik}/{accession_number}/{primary_document}")
        
        # Pattern 2: Common document name patterns
        company_lower = filing_info['company'].lower()
        form_type = filing_info['form_type']
        filing_date = filing_info['filing_date']
        
        # Extract year and month from filing date
        year = filing_date[:4]
        month = filing_date[5:7]
        day = filing_date[8:10]
        
        # Common document name patterns
        common_patterns = [
            f"{company_lower}-{year}{month}{day}.htm",
            f"{company_lower}-{year}{month}{day}.html",
            f"{company_lower}-{year}{month}.htm",
            f"{company_lower}-{year}{month}.html",
            f"{company_lower}-{year}.htm",
            f"{company_lower}-{year}.html",
            f"{form_type.lower()}-{year}{month}{day}.htm",
            f"{form_type.lower()}-{year}{month}{day}.html",
            f"{form_type.lower()}-{year}{month}.htm",
            f"{form_type.lower()}-{year}{month}.html",
            f"{form_type.lower()}-{year}.htm",
            f"{form_type.lower()}-{year}.html",
            "index.htm",
            "index.html",
            "main.htm",
            "main.html"
        ]
        
        for pattern in common_patterns:
            url_patterns.append(f"{self.filing_url}{cik}/{accession_number}/{pattern}")
        
        return url_patterns
    
    def download_filing(self, filing_info: Dict) -> Optional[str]:
        """
        Download a single filing document with multiple URL attempts
        
        Args:
            filing_info: Dictionary containing filing information
            
        Returns:
            Path to downloaded file or None if failed
        """
        url_patterns = self.construct_filing_url(filing_info)
        
        # Create filename
        company = filing_info['company']
        form_type = filing_info['form_type']
        filing_date = filing_info['filing_date']
        accession = filing_info['accession_number']
        
        filename = f"{company}{form_type}{filing_date}_{accession}.html"
        filepath = self.data_dir / company / filename
        
        # Create company directory
        (self.data_dir / company).mkdir(exist_ok=True)
        
        # Skip if file already exists
        if filepath.exists():
            logger.info(f"File already exists: {filename}")
            return str(filepath)
        
        # Try each URL pattern
        for i, url in enumerate(url_patterns):
            try:
                logger.info(f"Trying URL {i+1}/{len(url_patterns)}: {url}")
                
                # Download with appropriate headers
                response = requests.get(url, headers=self.filing_headers, timeout=30)
                
                if response.status_code == 200:
                    # Save the filing
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    
                    logger.info(f"Downloaded: {filename} (URL pattern {i+1})")
                    time.sleep(self.rate_limit_delay)
                    return str(filepath)
                else:
                    logger.info(f"URL {i+1} returned status {response.status_code}")
                    
            except requests.RequestException as e:
                logger.info(f"URL {i+1} failed: {e}")
                continue
        
        # If all patterns failed, try to get the filing index first
        try:
            index_url = f"{self.filing_url}{filing_info.get('cik', self.companies[filing_info['company']])}/{filing_info['accession_number'].replace('-', '')}/index.htm"
            logger.info(f"Trying index URL: {index_url}")
            
            response = requests.get(index_url, headers=self.filing_headers, timeout=30)
            if response.status_code == 200:
                # Parse the index to find the main document
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for links to main documents
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if any(keyword in href.lower() for keyword in ['10k', '10q', 'main', 'index']):
                        main_url = f"{self.filing_url}{filing_info.get('cik', self.companies[filing_info['company']])}/{filing_info['accession_number'].replace('-', '')}/{href}"
                        
                        try:
                            logger.info(f"Trying main document URL: {main_url}")
                            main_response = requests.get(main_url, headers=self.filing_headers, timeout=30)
                            if main_response.status_code == 200:
                                with open(filepath, 'w', encoding='utf-8') as f:
                                    f.write(main_response.text)
                                
                                logger.info(f"Downloaded: {filename} (via index)")
                                time.sleep(self.rate_limit_delay)
                                return str(filepath)
                        except requests.RequestException as e:
                            logger.info(f"Main document URL failed: {e}")
                            continue
        except Exception as e:
            logger.info(f"Index approach failed: {e}")
        
        logger.error(f"Error downloading {filename}: All URL patterns failed")
        return None
    
    def save_filing_metadata(self, all_filings: List[Dict]):
        """
        Save filing metadata to JSON and CSV files
        
        Args:
            all_filings: List of all filing dictionaries
        """
        # Save as JSON
        metadata_json = self.data_dir / "filing_metadata.json"
        with open(metadata_json, 'w') as f:
            json.dump(all_filings, f, indent=2)
        
        # Save as CSV for easy analysis
        metadata_csv = self.data_dir / "filing_metadata.csv"
        df = pd.DataFrame(all_filings)
        df.to_csv(metadata_csv, index=False)
        
        logger.info(f"Saved metadata: {len(all_filings)} filings")
    
    def get_filing_statistics(self, all_filings: List[Dict]) -> Dict:
        """
        Generate statistics about downloaded filings
        
        Args:
            all_filings: List of all filing dictionaries
            
        Returns:
            Dictionary containing filing statistics
        """
        stats = {
            'total_filings': len(all_filings),
            'by_company': {},
            'by_form_type': {},
            'by_year': {},
            'date_range': {
                'earliest': min([f['filing_date'] for f in all_filings]) if all_filings else None,
                'latest': max([f['filing_date'] for f in all_filings]) if all_filings else None
            }
        }
        
        for filing in all_filings:
            company = filing['company']
            form_type = filing['form_type']
            year = filing['filing_date'][:4]
            
            # Count by company
            stats['by_company'][company] = stats['by_company'].get(company, 0) + 1
            
            # Count by form type
            stats['by_form_type'][form_type] = stats['by_form_type'].get(form_type, 0) + 1
            
            # Count by year
            stats['by_year'][year] = stats['by_year'].get(year, 0) + 1
        
        return stats
    
    def test_single_filing_download(self, company_symbol: str, filing_date: str = None):
        """
        Test downloading a single filing for debugging purposes
        
        Args:
            company_symbol: Company symbol (e.g., 'AAPL')
            filing_date: Specific filing date to test (optional)
        """
        if company_symbol not in self.companies:
            logger.error(f"Company {company_symbol} not found in target companies")
            return
        
        cik = self.companies[company_symbol]
        logger.info(f"Testing single filing download for {company_symbol} (CIK: {cik})")
        
        # Get company submissions
        submissions = self.get_company_submissions(cik)
        if not submissions:
            logger.error(f"No submissions found for {company_symbol}")
            return
        
        # Filter for target filings
        company_filings = self.filter_filings(submissions, company_symbol)
        if not company_filings:
            logger.error(f"No filings found for {company_symbol}")
            return
        
        # If specific date provided, filter to that date
        if filing_date:
            company_filings = [f for f in company_filings if f['filing_date'] == filing_date]
            if not company_filings:
                logger.error(f"No filings found for {company_symbol} on {filing_date}")
                return
        
        # Test the first filing
        test_filing = company_filings[0]
        logger.info(f"Testing filing: {test_filing}")
        
        # Test URL construction
        url_patterns = self.construct_filing_url(test_filing)
        logger.info(f"Generated {len(url_patterns)} URL patterns:")
        for i, url in enumerate(url_patterns[:5]):  # Show first 5 patterns
            logger.info(f"  Pattern {i+1}: {url}")
        
        # Test download
        result = self.download_filing(test_filing)
        if result:
            logger.info(f"SUCCESS: Downloaded to {result}")
        else:
            logger.error("FAILED: Could not download filing")
    
    def scrape_all_filings(self) -> Dict:
        """
        Main method to scrape all MAG7 company filings
        
        Returns:
            Dictionary containing scraping results and statistics
        """
        logger.info("Starting SEC filing scraper for MAG7 companies")
        logger.info(f"Target companies: {list(self.companies.keys())}")
        logger.info(f"Filing types: {self.filing_types}")
        logger.info(f"Date range: {self.start_date} to {self.end_date}")
        
        all_filings = []
        download_results = []
        
        for company_symbol, cik in self.companies.items():
            logger.info(f"\nProcessing {company_symbol} (CIK: {cik})")
            
            # Get company submissions
            submissions = self.get_company_submissions(cik)
            if not submissions:
                logger.warning(f"No submissions found for {company_symbol}")
                continue
            
            # Filter for target filings
            company_filings = self.filter_filings(submissions, company_symbol)
            logger.info(f"Found {len(company_filings)} filings for {company_symbol}")
            
            # Download each filing
            for filing_info in company_filings:
                all_filings.append(filing_info)
                filepath = self.download_filing(filing_info)
                
                download_results.append({
                    'company': company_symbol,
                    'form_type': filing_info['form_type'],
                    'filing_date': filing_info['filing_date'],
                    'success': filepath is not None,
                    'filepath': filepath
                })
        
        # Save metadata
        self.save_filing_metadata(all_filings)
        
        # Generate statistics
        stats = self.get_filing_statistics(all_filings)
        
        # Save download results
        results_file = self.data_dir / "download_results.json"
        with open(results_file, 'w') as f:
            json.dump(download_results, f, indent=2)
        
        # Print summary
        logger.info(f"\n{'='*50}")
        logger.info("SCRAPING COMPLETE")
        logger.info(f"{'='*50}")
        logger.info(f"Total filings found: {stats['total_filings']}")
        logger.info(f"Date range: {stats['date_range']['earliest']} to {stats['date_range']['latest']}")
        logger.info(f"Successful downloads: {sum(1 for r in download_results if r['success'])}")
        logger.info(f"Failed downloads: {sum(1 for r in download_results if not r['success'])}")
        logger.info(f"\nBy company:")
        for company, count in stats['by_company'].items():
            logger.info(f"  {company}: {count} filings")
        logger.info(f"\nBy form type:")
        for form_type, count in stats['by_form_type'].items():
            logger.info(f"  {form_type}: {count} filings")
        
        return {
            'filings': all_filings,
            'download_results': download_results,
            'statistics': stats
        }

def main():
    """
    Main function to run the SEC filing scraper
    """
    # Initialize scraper with your contact information
    # IMPORTANT: Replace with your actual company name and email
    scraper = SECFilingScraper(user_agent="YourCompany contact@yourcompany.com")
    
    # Uncomment the line below to test a single filing download
    # scraper.test_single_filing_download("AAPL", "2023-11-03")
    
    # Run the scraper
    results = scraper.scrape_all_filings()
    
    # Print final summary
    print(f"\nScraping completed!")
    print(f"Data saved to: {scraper.data_dir}")
    print(f"Check filing_metadata.csv for a summary of all downloaded files")

if __name__ == "__main__":
    main()