from typing import List
import os
import pandas as pd
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from llama_index.embeddings.gemini import GeminiEmbedding
import logging

# Configure logger
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws")
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "models/embedding-001")

# Initialize the embedding model
embed_model = GeminiEmbedding(
    model_name=GEMINI_MODEL_NAME, 
    api_key=GOOGLE_API_KEY, 
    title="this is a document"
)

def generate_embeddings(text: str) -> List[float]:
    """
    Generate embeddings for the input text using Gemini's embedding model.
    
    Args:
        text: The text to generate embeddings for
        
    Returns:
        List of embedding values
    """
    text = text.replace("\n", " ")  # Remove newline characters for clean input
    return embed_model.get_text_embedding(text)

def create_pinecone_index(index_name: str, dimension: int = 768):
    """
    Create a Pinecone index with integrated embeddings if it doesn't already exist.
    
    Args:
        index_name: Name of the Pinecone index
        dimension: Dimension of the embeddings (default 768)
        
    Returns:
        Pinecone index object
    """
    pc_client = Pinecone(api_key=PINECONE_API_KEY)
    
    try:
        # List existing indexes to test connection
        existing_indexes = [index.name for index in pc_client.list_indexes()]
        logger.info(f"Successfully connected to Pinecone. Found {len(existing_indexes)} indexes")
    except Exception as e:
        logger.error(f"Failed to connect to Pinecone: {e}")
        raise
    
    # Check if index exists
    if index_name not in existing_indexes:
        logger.info(f"Creating new Pinecone index with integrated embeddings: {index_name}")
        pc_client.create_index_for_model(
            name=index_name,
            cloud=PINECONE_CLOUD,
            region=PINECONE_REGION,
            embed={
                "model": "llama-text-embed-v2",
                "field_map": {"text": "chunk_text"}
            }
        )
        logger.info(f"✅ Created new index: {index_name} with integrated embeddings")
    else:
        logger.info(f"Using existing Pinecone index: {index_name}")
    
    return pc_client.Index(index_name)

def load_and_upload_data(xlsx_path: str, index_name: str, batch_size: int = 100, dimension: int = 768):
    """
    Load data from an XLSX file with Type, Question, Answer format and 
    upload embeddings to the Pinecone index.
    
    Args:
        xlsx_path: Path to the Excel file
        index_name: Name of the Pinecone index
        batch_size: Number of vectors to upload in each batch
        dimension: Dimension of the embeddings (default 768)
        
    Returns:
        Dictionary with message about the operation result
    """
    if not os.path.exists(xlsx_path):
        raise FileNotFoundError(f"File not found: {xlsx_path}")
    
    logger.info(f"Creating/checking Pinecone index {index_name} with dimension {dimension}")
    index = create_pinecone_index(index_name, dimension)
    logger.info("Index creation/check completed.")
    
    try:
        sheets = pd.read_excel(xlsx_path, sheet_name=None)
        logger.info(f"Excel file loaded successfully with {len(sheets)} sheets")
        
        all_data = []
        for sheet_name, data in sheets.items():
            logger.info(f"Processing sheet: {sheet_name} with {len(data)} rows")
            for row_index, row in data.iterrows():
                # Check if the required columns exist
                if all(col in row.index for col in ['Type', 'Question', 'Answer']):
                    # Combine Question and Answer for embedding
                    combined_text = f"Type: {row['Type']}\nQuestion: {row['Question']}\nAnswer: {row['Answer']}"
                    
                    all_data.append({
                        "id": f"{sheet_name}-{row_index}",
                        "metadata": {
                            "type": row["Type"],
                            "question": row["Question"],
                            "answer": row["Answer"],
                            "sheet_name": sheet_name
                        },
                        "text": combined_text
                    })
                else:
                    logger.warning(f"Row {row_index} in sheet '{sheet_name}' is missing required columns")
        
        logger.info(f"Total data points to embed: {len(all_data)}")
        
        embeddings_list = []
        for i, doc in enumerate(all_data):
            if i % 10 == 0:
                logger.info(f"Generating embeddings: {i}/{len(all_data)}")
            
            embedding = generate_embeddings(doc["text"])
            embeddings_list.append({
                "id": doc["id"],
                "values": embedding,
                "metadata": doc["metadata"]
            })
        
        # Upload in batches
        for i in range(0, len(embeddings_list), batch_size):
            batch = embeddings_list[i:i + batch_size]
            logger.info(f"Uploading batch {i//batch_size + 1}/{(len(embeddings_list) + batch_size - 1)//batch_size}")
            index.upsert(vectors=batch)
        
        logger.info(f"Successfully uploaded {len(embeddings_list)} records to Pinecone index {index_name}")
        return {"message": f"Successfully uploaded {len(embeddings_list)} records to the Pinecone index."}
    
    except Exception as e:
        logger.error(f"Error processing file {xlsx_path}: {str(e)}")
        raise

def load_and_upload_all_chunks(json_path: str, index_name: str, batch_size: int = 100, dimension: int = 768):
    """
    Load all chunks from all_chunks.json and upload to Pinecone using integrated embeddings.

    Args:
        json_path: Path to all_chunks.json
        index_name: Name of the Pinecone index
        batch_size: Number of vectors to upload in each batch
        dimension: Dimension of the embeddings (default 768)

    Returns:
        Dictionary with message about the operation result
    """
    import json
    from tqdm import tqdm

    if not os.path.exists(json_path):
        raise FileNotFoundError(f"File not found: {json_path}")

    logger.info(f"Creating/checking Pinecone index {index_name} with integrated embeddings")
    index = create_pinecone_index(index_name, dimension)
    logger.info("Index creation/check completed.")

    with open(json_path, "r", encoding="utf-8") as f:
        all_chunks = json.load(f)

    logger.info(f"Loaded {len(all_chunks)} chunks from {json_path}")

    # Prepare records for integrated embedding upsert
    records = []
    MAX_CHUNK_SIZE = 35000  # bytes, for safety under 36,000 byte API limit
    
    for i, chunk in enumerate(tqdm(all_chunks, desc="Preparing chunks")):
        text = chunk["text"]
        if len(text.encode("utf-8")) > MAX_CHUNK_SIZE:
            logger.warning(f"Skipping chunk {chunk.get('chunk_id', 'unknown')} from {chunk.get('source_file', 'unknown')} - too large ({len(text.encode('utf-8'))} bytes)")
            continue
        
        # Create structured ID
        chunk_id = chunk.get("chunk_id", f"chunk_{i}")
        
        # Prepare metadata
        metadata = {
            "document_id": chunk.get("company", "unknown"),
            "document_title": f"{chunk.get('company', 'Unknown')} {chunk.get('form_type', 'Filing')}",
            "chunk_number": chunk.get("chunk_index", i),
            "document_url": build_sec_url(
                chunk.get("company"), 
                chunk.get("accession_number"), 
                chunk.get("source_file")
            ),
            "created_at": chunk.get("filing_date", "unknown"),
            "document_type": "sec_filing",
            "company": chunk.get("company"),
            "form_type": chunk.get("form_type"),
            "filing_date": chunk.get("filing_date"),
            "report_date": chunk.get("report_date"),
            "accession_number": chunk.get("accession_number"),
            "section": chunk.get("section"),
            "subsection": chunk.get("subsection"),
            "source_file": chunk.get("source_file")
        }
        
        # Add the record with raw text (Pinecone will convert to vector)
        records.append({
            "_id": chunk_id,
            "chunk_text": text,  # This field will be converted to vector by Pinecone
            **metadata
        })

    logger.info(f"Prepared {len(records)} records for upload")

    # Upload in batches using integrated embeddings
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        logger.info(f"Uploading batch {i//batch_size + 1}/{(len(records) + batch_size - 1)//batch_size}")
        
        try:
            index.upsert_records(
                namespace="mag7-financial-data",
                records=batch
            )
            logger.info(f"✅ Successfully uploaded batch {i//batch_size + 1}")
        except Exception as e:
            logger.error(f"❌ Failed to upload batch {i//batch_size + 1}: {e}")
            raise

    logger.info(f"Successfully uploaded {len(records)} records to Pinecone index {index_name}")
    return {"message": f"Successfully uploaded {len(records)} records to the Pinecone index using integrated embeddings."}

# Example usage:
if __name__ == "__main__":
    # Configure logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test the function
    test_file = r"D:\repo\llamaindex-poc\Ujjivan small FB.xlsx"
    if os.path.exists(test_file):
        result = load_and_upload_data(test_file, "test-embeddings-gemini")
        print(result["message"])
    else:
        print(f"Test file not found. Please update the path for testing.")

    # To upload all chunks from processed_filings/all_chunks.json:
    all_chunks_path = os.path.join("processed_filings", "all_chunks.json")
    if os.path.exists(all_chunks_path):
        result = load_and_upload_all_chunks(all_chunks_path, "mag7-financial-intelligence-2025")
        print(result["message"])
    else:
        print(f"all_chunks.json not found at {all_chunks_path}. Please generate it first.")