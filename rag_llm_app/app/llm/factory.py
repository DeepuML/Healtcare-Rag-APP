"""Factory for creating LLM generators based on configuration"""

from app.config import settings
from app.utils import get_logger

logger = get_logger(__name__)


def get_generator():
    """
    Factory function to get the appropriate LLM generator based on MODEL_BACKEND setting
    
    Returns:
        Generator instance (LocalLLMGenerator, OpenAIGenerator, or GeminiGenerator)
    """
    backend = settings.MODEL_BACKEND
    
    logger.info(f"Creating LLM generator for backend: {backend}")
    
    if backend == "local":
        from .local_generator import LocalLLMGenerator
        return LocalLLMGenerator()
    elif backend == "api":
        from .generator import OpenAIGenerator
        return OpenAIGenerator()
    elif backend == "gemini":
        from .gemini_generator import GeminiGenerator
        return GeminiGenerator()
    else:
        raise ValueError(
            f"Invalid MODEL_BACKEND: {backend}. Must be 'local', 'api', or 'gemini'"
        )
