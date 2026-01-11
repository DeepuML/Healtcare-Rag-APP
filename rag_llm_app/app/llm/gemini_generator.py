"""Gemini API LLM Generator for text generation and question answering"""

import logging
from typing import Optional
import google.generativeai as genai

from app.config import settings
from app.utils import get_logger

logger = get_logger(__name__)


class GeminiGenerator:
    """LLM Generator using Google Gemini API for text generation"""
    
    def __init__(self, model: str = None):
        """
        Initialize Gemini Generator
        
        Args:
            model: Model name (default: from settings)
        """
        self.model = model or settings.GEMINI_LLM_MODEL
        self.api_key = settings.GEMINI_API_KEY
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Configure Gemini API
        genai.configure(api_key=self.api_key)
        
        # Initialize the model
        self.client = genai.GenerativeModel(self.model)
        
        logger.info(f"GeminiGenerator initialized with model: {self.model}")
        logger.info(f"Temperature: {self.temperature}, Max tokens: {self.max_tokens}")
    
    def generate(self, prompt: str, context: Optional[str] = None) -> str:
        """
        Generate text using Gemini
        
        Args:
            prompt: The prompt/question to answer
            context: Optional context/documents to use
            
        Returns:
            Generated text response
        """
        try:
            # Build the full prompt with context if provided
            if context:
                full_prompt = f"""Based on the following context, answer the question.

Context:
{context}

Question: {prompt}

Answer:"""
            else:
                full_prompt = prompt
            
            # Generate response
            response = self.client.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                )
            )
            
            return response.text
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise
    
    def answer_question(self, question: str, context: str = "") -> str:
        """
        Answer a question based on provided context
        
        Args:
            question: The question to answer
            context: Relevant context/documents
            
        Returns:
            Answer text
        """
        return self.generate(question, context)
    
    def summarize(self, text: str) -> str:
        """
        Summarize provided text
        
        Args:
            text: Text to summarize
            
        Returns:
            Summary text
        """
        prompt = f"Please provide a concise summary of the following text:\n\n{text}"
        return self.generate(prompt)
