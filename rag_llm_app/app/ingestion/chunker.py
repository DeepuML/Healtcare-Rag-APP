"""Text chunking with sliding window sentence splitter"""

import re
from typing import List, Dict
from spacy.lang.en import English
from tqdm import tqdm
from app.config import settings
from app.utils import get_logger

logger = get_logger(__name__)


class TextChunker:
    """Chunk text into smaller pieces using sentence-based splitting"""
    
    def __init__(self, chunk_size: int = None, min_token_length: int = None):
        """
        Initialize the text chunker
        
        Args:
            chunk_size: Number of sentences per chunk
            min_token_length: Minimum token length to keep a chunk
        """
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.min_token_length = min_token_length or settings.MIN_TOKEN_LENGTH
        
        # Initialize spaCy for sentence segmentation
        self.nlp = English()
        self.nlp.add_pipe("sentencizer")
        
        logger.info(f"TextChunker initialized with chunk_size={self.chunk_size}, min_token_length={self.min_token_length}")
    
    def split_into_sentences(self, pages_and_texts: List[Dict]) -> List[Dict]:
        """
        Split page texts into sentences using spaCy
        
        Args:
            pages_and_texts: List of page dictionaries
            
        Returns:
            Updated list with sentences added
        """
        logger.info("Splitting text into sentences...")
        
        for item in tqdm(pages_and_texts, desc="Sentence splitting"):
            doc = self.nlp(item["text"])
            item["sentences"] = [str(sent) for sent in doc.sents]
            item["page_sentence_count_spacy"] = len(item["sentences"])
        
        return pages_and_texts
    
    @staticmethod
    def split_list(input_list: List[str], slice_size: int) -> List[List[str]]:
        """
        Splits the input_list into sublists of size slice_size
        
        Args:
            input_list: List to split
            slice_size: Size of each chunk
            
        Returns:
            List of sublists
        """
        return [input_list[i:i + slice_size] for i in range(0, len(input_list), slice_size)]
    
    def create_chunks(self, pages_and_texts: List[Dict]) -> List[Dict]:
        """
        Create chunks from sentences
        
        Args:
            pages_and_texts: List of page dictionaries with sentences
            
        Returns:
            List of chunk dictionaries
        """
        logger.info("Creating text chunks...")
        
        # First split into sentences
        pages_and_texts = self.split_into_sentences(pages_and_texts)
        
        # Then create chunks
        pages_and_chunks = []
        
        for item in tqdm(pages_and_texts, desc="Creating chunks"):
            sentence_chunks = self.split_list(item["sentences"], self.chunk_size)
            
            for sentence_chunk in sentence_chunks:
                chunk_dict = {}
                chunk_dict["page_number"] = item["page_number"]
                
                # Join sentences into a chunk
                joined_sentence_chunk = "".join(sentence_chunk).replace("  ", " ").strip()
                joined_sentence_chunk = re.sub(r'\.([A-Z])', r'. \1', joined_sentence_chunk)
                chunk_dict["sentence_chunk"] = joined_sentence_chunk
                
                # Get stats about the chunk
                chunk_dict["chunk_char_count"] = len(joined_sentence_chunk)
                chunk_dict["chunk_word_count"] = len(joined_sentence_chunk.split(" "))
                chunk_dict["chunk_token_count"] = len(joined_sentence_chunk) / 4
                
                pages_and_chunks.append(chunk_dict)
        
        # Filter out chunks that are too small
        filtered_chunks = [
            chunk for chunk in pages_and_chunks 
            if chunk["chunk_token_count"] > self.min_token_length
        ]
        
        logger.info(f"Created {len(filtered_chunks)} chunks (filtered from {len(pages_and_chunks)})")
        
        return filtered_chunks
