"""PDF document loader using PyMuPDF"""

import fitz  # PyMuPDF
import requests
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm
from app.config import settings
from app.utils import get_logger

logger = get_logger(__name__)


class PDFLoader:
    """Load and extract text from PDF documents"""
    
    @staticmethod
    def text_formatter(text: str) -> str:
        """
        Performs minor formatting on text
        
        Args:
            text: Raw text to format
            
        Returns:
            Cleaned text
        """
        cleaned_text = text.replace("\n", " ").strip()
        return cleaned_text
    
    @staticmethod
    def download_pdf(url: str, save_path: str | Path) -> bool:
        """
        Download PDF from URL if it doesn't exist
        
        Args:
            url: URL to download PDF from
            save_path: Path to save the PDF
            
        Returns:
            True if downloaded or already exists
        """
        save_path = Path(save_path)
        
        if save_path.exists():
            logger.info(f"File {save_path} already exists")
            return True
        
        logger.info(f"Downloading PDF from {url}...")
        
        try:
            response = requests.get(url)
            
            if response.status_code == 200:
                save_path.parent.mkdir(parents=True, exist_ok=True)
                with open(save_path, "wb") as file:
                    file.write(response.content)
                logger.info(f"PDF downloaded and saved as {save_path}")
                return True
            else:
                logger.error(f"Failed to download. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error downloading PDF: {e}")
            return False
    
    @staticmethod
    def load_pdf(pdf_path: str | Path, page_offset: int = None) -> List[Dict]:
        """
        Opens a PDF file and reads its text content page by page
        
        Args:
            pdf_path: Path to the PDF file
            page_offset: Offset to adjust page numbers (e.g., -41 if PDF starts on page 42)
            
        Returns:
            List of dictionaries containing page information and text
        """
        pdf_path = Path(pdf_path)
        page_offset = page_offset if page_offset is not None else settings.PAGE_NUMBER_OFFSET
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        logger.info(f"Loading PDF: {pdf_path}")
        
        doc = fitz.open(pdf_path)
        pages_and_texts = []
        
        for page_number, page in tqdm(enumerate(doc), total=len(doc), desc="Loading pages"):
            text = page.get_text()
            text = PDFLoader.text_formatter(text)
            
            pages_and_texts.append({
                "page_number": page_number + page_offset,
                "page_char_count": len(text),
                "page_word_count": len(text.split(" ")),
                "page_sentence_count_raw": len(text.split(". ")),
                "page_token_count": len(text) / 4,  # 1 token ≈ 4 chars
                "text": text
            })
        
        doc.close()
        logger.info(f"Loaded {len(pages_and_texts)} pages from PDF")
        
        return pages_and_texts
