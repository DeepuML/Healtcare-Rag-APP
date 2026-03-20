"""
Document ingestion script for the Healthcare RAG pipeline.

Reads a PDF file page by page, splits each page's text into
sentence-level chunks, generates local embeddings (all-mpnet-base-v2),
and writes the results to:

* A local CSV file (``rag_llm_app/data/documents/text_chunks_and_embeddings_df.csv``)
* Supabase ``chunks`` table (when SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY
  are set in the environment)

Usage::

    python ingest.py

Environment variables (optional – falls back to CSV-only if absent):
    SUPABASE_URL              - Supabase project URL
    SUPABASE_SERVICE_ROLE_KEY - Supabase service-role key
"""

import os, uuid, re, sys
from pathlib import Path
import fitz  # PyMuPDF
import tiktoken
from supabase import create_client, Client
from tqdm import tqdm
from dotenv import load_dotenv, find_dotenv

# Add rag_llm_app to path for local embedder
sys.path.insert(0, str(Path(__file__).parent / "rag_llm_app"))
from app.embeddings.local_embedder import LocalEmbedder

# ---- Load environment
load_dotenv(find_dotenv(usecwd=True))

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

# ---- Config
PDF_PATH = "rag_llm_app/data/documents/Human-Nutrition-2020-Edition-1598491699.pdf"
DOC_ID = "nutrition-v1"
EMBED_MODEL = "text-embedding-3-small"
BATCH_EMBED = 100
BATCH_INSERT = 200

# Sentence chunking params
SENTS_PER_CHUNK = 20
SENT_OVERLAP = 2
MAX_TOKENS = 1300
MIN_TOKENS = 50

enc = tiktoken.get_encoding("cl100k_base")

def clean_text(t: str) -> str:
    """
    Normalize raw PDF text for downstream processing.

    Removes carriage returns, joins words broken across line-breaks
    (e.g. "nutri-\\ntion" → "nutrition"), collapses consecutive
    whitespace, and strips leading/trailing whitespace.

    Args:
        t: Raw text extracted from a single PDF page.

    Returns:
        Cleaned, single-line text string.
    """
    # Remove carriage returns
    t = t.replace("\r", " ")
    # Join words hyphenated across line breaks (e.g. "nutri-\n tion" → "nutrition")
    t = re.sub(r"-\s*\n\s*", "", t)
    # Drop trailing spaces before newlines
    t = re.sub(r"\s+\n", "\n", t)
    # Collapse multiple spaces/tabs into a single space
    t = re.sub(r"[ \t]+", " ", t)
    # Replace remaining newlines with spaces and strip edges
    t = t.replace("\n", " ").strip()
    return t

def split_sentences(text: str):
    """
    Split a block of text into individual sentences.

    Uses a simple regex look-behind on sentence-ending punctuation
    (``.``, ``!``, ``?``).  Suitable for well-formed prose.

    Args:
        text: Cleaned, single-line text to split.

    Returns:
        List of non-empty sentence strings.
    """
    # Split on whitespace that follows sentence-ending punctuation
    sents = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sents if s.strip()]

def chunk_page_by_sentences(text: str,
                             sents_per_chunk: int = SENTS_PER_CHUNK,
                             overlap: int = SENT_OVERLAP,
                             max_tokens: int = MAX_TOKENS,
                             min_tokens: int = MIN_TOKENS):
    """
    Yield sentence-level chunks from a single page of text.

    Uses a sliding window over the sentence list with configurable
    overlap.  Chunks that exceed ``max_tokens`` are trimmed by
    dropping trailing sentences; chunks below ``min_tokens`` are
    discarded entirely.

    Args:
        text:            Cleaned text for one PDF page.
        sents_per_chunk: Target number of sentences per chunk.
        overlap:         Number of sentences shared between adjacent chunks.
        max_tokens:      Hard token ceiling per chunk (0 = no limit).
        min_tokens:      Minimum token count; shorter chunks are skipped.

    Yields:
        str: Individual text chunk strings.
    """
    sents = split_sentences(text)
    i = 0
    # Step size accounts for the overlap between consecutive windows
    step = max(1, sents_per_chunk - overlap)

    while i < len(sents):
        piece = sents[i:i + sents_per_chunk]
        if not piece:
            break

        chunk = " ".join(piece)

        # Enforce token ceiling by dropping sentences from the end
        ids = enc.encode(chunk)
        while max_tokens and len(ids) > max_tokens and len(piece) > 1:
            piece = piece[:-1]
            chunk = " ".join(piece)
            ids = enc.encode(chunk)

        # Only yield chunks that meet the minimum token threshold
        if len(ids) >= min_tokens:
            yield chunk

        i += step

def pdf_pages(path: str):
    """
    Yield cleaned text for every page of a PDF file.

    Args:
        path: Filesystem path to the PDF file.

    Yields:
        Tuple[int, str]: ``(1-based page number, cleaned page text)``.
            Pages with no extractable text yield an empty string.
    """
    doc = fitz.open(path)
    try:
        for i in range(len(doc)):
            txt = doc[i].get_text("text") or ""
            yield (i + 1, clean_text(txt))
    finally:
        doc.close()

def main():
    """
    Run the full ingestion pipeline.

    Steps performed:
    1. Connect to Supabase (if credentials are available) and clear any
       existing rows for the current ``DOC_ID``.
    2. Read the PDF page by page and collect raw text.
    3. Split each page into sentence-level chunks (with overlap).
    4. Generate dense embeddings for all chunks using the local
       sentence-transformers model (``all-mpnet-base-v2``).
    5. Save the chunks + embeddings to a local CSV file for use with
       the local retrieval pipeline.
    6. Upload rows to Supabase ``chunks`` table if credentials exist.
    """
    # Check if Supabase credentials are provided
    use_supabase = bool(SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY)
    
    if use_supabase:
        print("Using Supabase for storage")
        sb: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        # Optional: keep the table clean for this document
        sb.table("chunks").delete().eq("doc_id", DOC_ID).execute()
    else:
        print("Supabase credentials not found, will save to CSV only")
    
    print("Reading PDF by pages...")
    pages = list(pdf_pages(PDF_PATH))
    print(f"📄 Loaded {len(pages)} pages from PDF")
    
    # Build chunks with page metadata
    inputs, metas = [], []
    empty_pages = 0
    pages_with_chunks = 0
    print(f"Chunking ({SENTS_PER_CHUNK} sentences per chunk, {SENT_OVERLAP} overlap, min {MIN_TOKENS} tokens)...")
    
    for page_num, text in pages:
        if not text:
            empty_pages += 1
            continue
        
        page_chunks = 0
        for chunk in chunk_page_by_sentences(text):
            inputs.append(chunk)
            metas.append({"source": PDF_PATH, "page": page_num})
            page_chunks += 1
        
        if page_chunks > 0:
            pages_with_chunks += 1
            
    print(f"✅ Built {len(inputs)} chunks from {len(pages)} pages")
    print(f"   - Pages with text: {pages_with_chunks}")
    print(f"   - Empty pages skipped: {empty_pages}")
    print(f"   - Pages with text but no chunks (< {MIN_TOKENS} tokens): {len(pages) - empty_pages - pages_with_chunks}")
    
    # Generate embeddings using local model
    print("Generating embeddings with local model (all-mpnet-base-v2)...")
    embedder = LocalEmbedder()
    vectors = embedder.embed_chunks(inputs, batch_size=BATCH_EMBED, show_progress=True)
        
    # Prepare rows
    rows = []
    for idx, (content, emb, meta) in enumerate(zip(inputs, vectors, metas)):
        rows.append({
            "doc_id": DOC_ID,
            "chunk_index": idx,
            "content": content,
            "metadata": meta,      # contains {source, page}
            "embedding": emb
        })
    
    # Save to CSV for local use
    import pandas as pd
    csv_path = "rag_llm_app/data/documents/text_chunks_and_embeddings_df.csv"
    df = pd.DataFrame([
        {
            "sentence_chunk": row["content"],
            "page_number": row["metadata"]["page"],
            "chunk_token_count": len(row["content"].split()),
            "embedding": str(row["embedding"])  # Store as string representation
        }
        for row in rows
    ])
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    df.to_csv(csv_path, index=False)
    print(f"✅ Saved {len(rows)} chunks to {csv_path}")
    
    # Upload to Supabase if credentials are available
    if use_supabase:
        print("Uploading to Supabase...")
        try:
            for j in tqdm(range(0, len(rows), BATCH_INSERT), desc="Uploading"):
                sb.table("chunks").insert(rows[j:j + BATCH_INSERT]).execute()
            print(f"✅ Uploaded {len(rows)} chunks to Supabase for doc_id={DOC_ID}")
        except Exception as e:
            if "dimensions" in str(e).lower():
                print(f"\n⚠️  Supabase upload skipped: Table expects different embedding dimensions.")
                print(f"   Local model produces 768-dim embeddings, but Supabase table expects 1536-dim (OpenAI).")
                print(f"   Data is saved to CSV: {csv_path}")
            else:
                print(f"\n❌ Supabase upload failed: {e}")
                raise
    
    print(f"🎉 Done! Processed {len(rows)} chunks")

if __name__ == "__main__":
    main()