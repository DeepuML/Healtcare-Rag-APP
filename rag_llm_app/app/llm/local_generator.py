"""Local LLM generator using transformers (matching notebook implementation)"""

from typing import Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from app.config import settings
from app.utils import get_logger

logger = get_logger(__name__)


class LocalLLMGenerator:
    """Generate answers using local LLM models (Gemma, Mistral, etc.)"""
    
    def __init__(
        self,
        model: str = None,
        temperature: float = None,
        device: str = None,
        use_quantization: bool = None
    ):
        """
        Initialize the local LLM generator
        
        Args:
            model: HuggingFace model ID (e.g., google/gemma-7b-it)
            temperature: Sampling temperature
            device: Device to run on ('cuda' or 'cpu')
            use_quantization: Whether to use 4-bit quantization
        """
        self.model_id = model or settings.LOCAL_LLM_MODEL
        self.temperature = temperature or settings.LLM_TEMPERATURE
        self.device = device or settings.LLM_DEVICE
        self.use_quantization = use_quantization if use_quantization is not None else settings.USE_QUANTIZATION
        
        # Check CUDA availability
        if self.device == "cuda" and not torch.cuda.is_available():
            logger.warning("CUDA requested but not available, falling back to CPU")
            self.device = "cpu"
            self.use_quantization = False
        
        logger.info(f"Loading local LLM: {self.model_id}")
        logger.info(f"Device: {self.device}, Quantization: {self.use_quantization}")
        
        # Setup quantization config if needed
        quantization_config = None
        if self.use_quantization:
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16
            )
            logger.info("Using 4-bit quantization")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        
        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            torch_dtype=torch.float16,
            quantization_config=quantization_config,
            low_cpu_mem_usage=False,
            attn_implementation=settings.ATTENTION_IMPLEMENTATION
        )
        
        # Move to device if not using quantization (quantization handles this automatically)
        if not self.use_quantization:
            self.model.to(self.device)
        
        logger.info("LocalLLMGenerator initialized successfully")
    
    def create_prompt(self, query: str, context: str) -> str:
        """
        Create a RAG prompt with context and query
        
        Args:
            query: User question
            context: Retrieved context
            
        Returns:
            Formatted prompt
        """
        base_prompt = """Based on the following context items, please answer the query.
Give yourself room to think by extracting relevant passages from the context before answering the query.
Don't return the thinking, only return the answer.
Make sure your answers are as explanatory as possible.
Use the following examples as reference for the ideal answer style.

Example 1:
Query: What are the fat-soluble vitamins?
Answer: The fat-soluble vitamins include Vitamin A, Vitamin D, Vitamin E, and Vitamin K. These vitamins are absorbed along with fats in the diet and can be stored in the body's fatty tissue and liver for later use. Vitamin A is important for vision, immune function, and skin health. Vitamin D plays a critical role in calcium absorption and bone health. Vitamin E acts as an antioxidant, protecting cells from damage. Vitamin K is essential for blood clotting and bone metabolism.

Example 2:
Query: What are the causes of type 2 diabetes?
Answer: Type 2 diabetes is often associated with overnutrition, particularly the overconsumption of calories leading to obesity. Factors include a diet high in refined sugars and saturated fats, which can lead to insulin resistance, a condition where the body's cells do not respond effectively to insulin. Over time, the pancreas cannot produce enough insulin to manage blood sugar levels, resulting in type 2 diabetes. Additionally, excessive caloric intake without sufficient physical activity exacerbates the risk by promoting weight gain and fat accumulation, particularly around the abdomen, further contributing to insulin resistance.

Example 3:
Query: What is the importance of hydration for physical performance?
Answer: Hydration is crucial for physical performance because water plays key roles in maintaining blood volume, regulating body temperature, and ensuring the transport of nutrients and oxygen to cells. Adequate hydration is essential for optimal muscle function, endurance, and recovery. Dehydration can lead to decreased performance, fatigue, and increased risk of heat-related illnesses, such as heat stroke. Drinking sufficient water before, during, and after exercise helps ensure peak physical performance and recovery.

Now use the following context items to answer the user query:
{context}

Relevant passages: <extract relevant passages from the context here>
User query: {query}
Answer:"""
        
        return base_prompt.format(context=context, query=query)
    
    def generate(
        self,
        query: str,
        context: str,
        max_tokens: int = None,
        format_answer: bool = True
    ) -> str:
        """
        Generate an answer based on query and context
        
        Args:
            query: User question
            context: Retrieved context
            max_tokens: Maximum tokens to generate
            format_answer: Whether to remove prompt from output
            
        Returns:
            Generated answer
        """
        max_tokens = max_tokens or settings.LLM_MAX_TOKENS
        
        # Create base prompt
        base_prompt = self.create_prompt(query, context)
        
        # Apply chat template for instruction-tuned models
        dialogue_template = [
            {"role": "user", "content": base_prompt}
        ]
        
        prompt = self.tokenizer.apply_chat_template(
            conversation=dialogue_template,
            tokenize=False,
            add_generation_prompt=True
        )
        
        logger.info(f"Generating answer for query: {query[:50]}...")
        
        try:
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
            # Generate
            outputs = self.model.generate(
                **inputs,
                temperature=self.temperature,
                do_sample=True,
                max_new_tokens=max_tokens
            )
            
            # Decode output
            answer = self.tokenizer.decode(outputs[0])
            
            # Format answer
            if format_answer:
                answer = answer.replace(prompt, "").strip()
                answer = answer.replace("<bos>", "").replace("<eos>", "").strip()
                answer = answer.replace("Sure, here is the answer to the user query:\n\n", "")
            
            logger.info("Answer generated successfully")
            return answer
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise
