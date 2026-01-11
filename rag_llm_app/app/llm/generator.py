"""OpenAI Chat Completion generator"""

from typing import List, Dict
from openai import OpenAI
from app.config import settings
from app.utils import get_logger

logger = get_logger(__name__)


class OpenAIGenerator:
    """Generate answers using OpenAI's Chat Completion API"""
    
    def __init__(self, model: str = None, temperature: float = None):
        """
        Initialize the generator
        
        Args:
            model: OpenAI model to use
            temperature: Sampling temperature
        """
        self.model = model or settings.LLM_MODEL
        self.temperature = temperature or settings.LLM_TEMPERATURE
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        logger.info(f"OpenAIGenerator initialized with model: {self.model}")
    
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
        max_tokens: int = None
    ) -> str:
        """
        Generate an answer based on query and context
        
        Args:
            query: User question
            context: Retrieved context
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated answer
        """
        max_tokens = max_tokens or settings.LLM_MAX_TOKENS
        
        prompt = self.create_prompt(query, context)
        
        logger.info(f"Generating answer for query: {query[:50]}...")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that answers questions based on provided context. Always cite the context when answering."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=max_tokens
            )
            
            answer = response.choices[0].message.content
            logger.info("Answer generated successfully")
            
            return answer
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise
