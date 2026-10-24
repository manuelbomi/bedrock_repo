"""Build FAISS index locally before deployment"""
import csv
import os
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_aws import BedrockEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()

REGION = "us-east-1"
CSV_PATH = "./buy_'n'_sell.csv"
FAISS_INDEX_PATH = "./faiss_index"


def load_faq_csv(path: str) -> List[Document]:
    """Load FAQ data from CSV file"""
    docs = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            q = row["question"].strip()
            a = row["answer"].strip()
            docs.append(Document(page_content=f"Q: {q}\nA: {a}"))
    return docs


def main():
    print("Building FAISS index...")

    # Load embeddings model
    print("Initializing Bedrock embeddings...")
    emb = BedrockEmbeddings(
        model_id="amazon.titan-embed-text-v2:0",
        region_name=os.getenv("AWS_REGION", REGION),
    )

    # Load FAQ documents
    print(f"Loading FAQ data from {CSV_PATH}...")
    docs = load_faq_csv(CSV_PATH)
    print(f"Loaded {len(docs)} FAQ documents")

    # Split documents
    print("Splitting documents into chunks...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    chunks = splitter.split_documents(docs)
    print(f"Created {len(chunks)} chunks")

    # Create FAISS index with batching to avoid throttling
    print("Creating FAISS index (this may take a few minutes)...")
    print("Processing embeddings in batches to avoid throttling...")

    # Process in smaller batches
    batch_size = 10
    all_vectors = []

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(len(chunks) + batch_size - 1)//batch_size}...")

        if i == 0:
            # Create initial store with first batch
            faq_store = FAISS.from_documents(batch, emb)
        else:
            # Add subsequent batches to existing store
            batch_store = FAISS.from_documents(batch, emb)
            faq_store.merge_from(batch_store)

        # Small delay to avoid throttling
        import time
        time.sleep(1)

    # Save the index
    print(f"Saving FAISS index to {FAISS_INDEX_PATH}...")
    faq_store.save_local(FAISS_INDEX_PATH)

    print("✓ FAISS index built successfully!")
    print(f"✓ Index saved to: {os.path.abspath(FAISS_INDEX_PATH)}")
    print(f"✓ Total documents indexed: {len(chunks)}")


if __name__ == "__main__":
    main()
