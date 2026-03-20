"""
LLM (Large Language Model) subpackage.

Provides answer-generation back-ends that take a user query and a
retrieved context string and produce a natural-language response.

Exports:
    OpenAIGenerator   - Generator backed by the OpenAI Chat Completions API.
    LocalLLMGenerator - Generator using a locally-running HuggingFace model
                        (e.g. Gemma, Mistral) via the ``transformers`` library.
    get_generator     - Factory function that selects the correct generator
                        based on the ``MODEL_BACKEND`` setting.
"""

from .generator import OpenAIGenerator
from .local_generator import LocalLLMGenerator
from .factory import get_generator

__all__ = ["OpenAIGenerator", "LocalLLMGenerator", "get_generator"]
