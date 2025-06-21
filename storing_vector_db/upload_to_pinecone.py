import os
import logging
from embeddings import load_and_upload_all_chunks

# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional, script will continue if not installed

def check_environment_variables():
    """Check if required environment variables are set"""
    required_vars = {
        "PINECONE_API_KEY": os.getenv("PINECONE_API_KEY"),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY")
    }
    
    missing_vars = []
    for var_name, var_value in required_vars.items():
        if not var_value or var_value == f"your_{var_name.lower()}_here":
            missing_vars.append(var_name)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in your .env file:")
        print("   PINECONE_API_KEY=your_actual_pinecone_key")
        print("   GOOGLE_API_KEY=your_actual_google_key")
        return False
    
    return True

def mask_key(key):
    """Mask API key for display (show only first and last 2 characters)"""
    if key and len(key) > 4:
        return key[:2] + "*" * (len(key)-4) + key[-2:]
    return "NOT SET"

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Check environment variables
    if not check_environment_variables():
        exit(1)
    
    # Display masked keys for verification
    print("🔐 Environment Variables Status:")
    print(f"   PINECONE_API_KEY: {mask_key(os.getenv('PINECONE_API_KEY'))}")
    print(f"   GOOGLE_API_KEY: {mask_key(os.getenv('GOOGLE_API_KEY'))}")
    print(f"   PINECONE_CLOUD: {os.getenv('PINECONE_CLOUD', 'aws')}")
    print(f"   PINECONE_REGION: {os.getenv('PINECONE_REGION', 'us-east-1')}")
    print()

    all_chunks_path = os.path.join("processed_filings", "all_chunks.json")
    index_name = "mag7-financial-intelligence-2025"

    if os.path.exists(all_chunks_path):
        print(f"📤 Uploading all chunks from {all_chunks_path} to Pinecone index '{index_name}'...")
        try:
            result = load_and_upload_all_chunks(all_chunks_path, index_name)
            print(f"✅ {result['message']}")
        except Exception as e:
            print(f"❌ Error uploading to Pinecone: {e}")
            print("Please check your API keys and network connection.")
    else:
        print(f"❌ all_chunks.json not found at {all_chunks_path}")
        print("Please generate it first by running the text processing pipeline:")
        print("   python -c \"from data_storing.text_cleaning import SECTextProcessor; processor = SECTextProcessor(); processor.process_all_filings()\"") 