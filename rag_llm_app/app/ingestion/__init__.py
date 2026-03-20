"""
Ingestion subpackage.

Provides utilities for loading PDF documents and splitting their text
into overlapping sentence-level chunks suitable for embedding.

Exports:
    PDFLoader   - Loads and extracts text from PDF files page by page.
    TextChunker - Splits extracted text into sentence-based chunks.
"""

from .loader import PDFLoader
from .chunker import TextChunker

__all__ = ["PDFLoader", "TextChunker"]
