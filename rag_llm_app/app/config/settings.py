"""Configuration settings loaded from environment variables"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    """Application settings"""
    
    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    # Model Backend Selection
    MODEL_BACKEND: str = os.getenv("MODEL_BACKEND", "local")  # "local", "api", or "gemini"
    
    # OpenAI (only needed if MODEL_BACKEND=api)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Gemini API (only needed if MODEL_BACKEND=gemini)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Local Embedding Configuration (sentence-transformers)
    LOCAL_EMBEDDING_MODEL: str = os.getenv("LOCAL_EMBEDDING_MODEL", "all-mpnet-base-v2")
    LOCAL_EMBEDDING_DIMENSION: int = int(os.getenv("LOCAL_EMBEDDING_DIMENSION", "768"))
    EMBEDDING_DEVICE: str = os.getenv("EMBEDDING_DEVICE", "cpu")
    
    # API Embedding Configuration (OpenAI)
    API_EMBEDDING_MODEL: str = os.getenv("API_EMBEDDING_MODEL", "text-embedding-3-small")
    API_EMBEDDING_DIMENSION: int = int(os.getenv("API_EMBEDDING_DIMENSION", "1536"))
    
    # Gemini Embedding Configuration
    GEMINI_EMBEDDING_MODEL: str = os.getenv("GEMINI_EMBEDDING_MODEL", "models/embedding-001")
    GEMINI_EMBEDDING_DIMENSION: int = int(os.getenv("GEMINI_EMBEDDING_DIMENSION", "768"))
    
    # Local LLM Configuration (Gemma, Mistral, etc.)
    LOCAL_LLM_MODEL: str = os.getenv("LOCAL_LLM_MODEL", "sshleifer/tiny-gpt2")
    USE_QUANTIZATION: bool = os.getenv("USE_QUANTIZATION", "False").lower() == "true"
    LLM_DEVICE: str = os.getenv("LLM_DEVICE", "cuda")
    ATTENTION_IMPLEMENTATION: str = os.getenv("ATTENTION_IMPLEMENTATION", "sdpa")

    # Retrieval mode
    RETRIEVER_MODE: str = os.getenv("RETRIEVER_MODE", "local")
    
    # API LLM Configuration (OpenAI)
    API_LLM_MODEL: str = os.getenv("API_LLM_MODEL", "gpt-4-turbo-preview")
    
    # Gemini LLM Configuration
    GEMINI_LLM_MODEL: str = os.getenv("GEMINI_LLM_MODEL", "gemini-2.0-flash")
    
    # Generation Parameters
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "512"))
    
    # Chunking Configuration
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "10"))
    MIN_TOKEN_LENGTH: int = int(os.getenv("MIN_TOKEN_LENGTH", "30"))
    PAGE_NUMBER_OFFSET: int = int(os.getenv("PAGE_NUMBER_OFFSET", "0"))
    
    # Retrieval Configuration
    TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", "5"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    DOCUMENTS_DIR: Path = DATA_DIR / "documents"
    
    @property
    def EMBEDDING_MODEL(self):
        """Get the appropriate embedding model based on backend"""
        if self.MODEL_BACKEND == "local":
            return self.LOCAL_EMBEDDING_MODEL
        if self.MODEL_BACKEND == "api":
            return self.API_EMBEDDING_MODEL
        return self.GEMINI_EMBEDDING_MODEL
    
    @property
    def EMBEDDING_DIMENSION(self):
        """Get the appropriate embedding dimension based on backend"""
        if self.MODEL_BACKEND == "local":
            return self.LOCAL_EMBEDDING_DIMENSION
        if self.MODEL_BACKEND == "api":
            return self.API_EMBEDDING_DIMENSION
        return self.GEMINI_EMBEDDING_DIMENSION
    
    @property
    def LLM_MODEL(self):
        """Get the appropriate LLM model based on backend"""
        if self.MODEL_BACKEND == "local":
            return self.LOCAL_LLM_MODEL
        if self.MODEL_BACKEND == "api":
            return self.API_LLM_MODEL
        return self.GEMINI_LLM_MODEL
    
    def validate(self):
        """Validate required settings"""
        # Always required
        required_fields = []

        # Require Supabase only when using Supabase retriever
        if self.RETRIEVER_MODE == "supabase":
            required_fields.extend([
                ("SUPABASE_URL", self.SUPABASE_URL),
                ("SUPABASE_SERVICE_ROLE_KEY", self.SUPABASE_SERVICE_ROLE_KEY),
            ])
        
        # Add API key requirement if using API backend
        if self.MODEL_BACKEND == "api":
            required_fields.append(("OPENAI_API_KEY", self.OPENAI_API_KEY))
        
        # Add Gemini key requirement if using Gemini backend
        if self.MODEL_BACKEND == "gemini":
            required_fields.append(("GEMINI_API_KEY", self.GEMINI_API_KEY))
        
        missing_fields = [field for field, value in required_fields if not value]
        
        if missing_fields:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_fields)}"
            )
        
        if self.MODEL_BACKEND not in ["local", "api", "gemini"]:
            raise ValueError(
                f"MODEL_BACKEND must be 'local', 'api', or 'gemini', got: {self.MODEL_BACKEND}"
            )

        if self.RETRIEVER_MODE not in ["local", "supabase"]:
            raise ValueError(
                f"RETRIEVER_MODE must be 'local' or 'supabase', got: {self.RETRIEVER_MODE}"
            )
        
        return True


# Create global settings instance
settings = Settings()
